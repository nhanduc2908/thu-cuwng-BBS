from datetime import date, timedelta
import sqlite3

import pytest

from app.database import Database
from app.modules.recommendations.engine import recommend_products


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "inventory.db")
    yield instance
    instance.close()


def create_item(database, minimum=3):
    return database.save_inventory_item(
        {
            "item_code": "FOOD-001",
            "name": "Thức ăn mèo",
            "category": "FOOD",
            "unit": "kg",
            "minimum_stock": minimum,
            "description": "",
        }
    )


def receive(database, item_id, batch_code, quantity, expiry_date, cost=100):
    return database.receive_inventory_stock(
        item_id,
        {
            "batch_code": batch_code,
            "quantity": quantity,
            "unit_cost": cost,
            "expiry_date": expiry_date,
            "occurred_on": date.today().isoformat(),
            "reference": "PO-1",
            "note": "",
        },
    )


def test_receiving_consumption_uses_fefo_and_keeps_ledger(database):
    item_id = create_item(database)
    today = date.today()
    later = (today + timedelta(days=60)).isoformat()
    sooner = (today + timedelta(days=10)).isoformat()
    receive(database, item_id, "B-LATER", 4, later)
    receive(database, item_id, "B-SOONER", 2, sooner)

    animal_id = database.save_animal(
        {
            "animal_code": "PET-1",
            "name": "Milo",
            "species": "Mèo",
            "sale_price": 1,
            "status": "AVAILABLE",
        }
    )
    movement_ids = database.consume_inventory_stock(
        item_id,
        {
            "quantity": 3,
            "animal_id": animal_id,
            "occurred_on": today.isoformat(),
        },
    )

    assert len(movement_ids) == 2
    batches = database.list_inventory_batches(item_id)
    assert [(row["batch_code"], row["quantity_remaining"]) for row in batches] == [
        ("B-SOONER", 0),
        ("B-LATER", 3),
    ]
    movements = database.list_inventory_movements(item_id)
    assert [row["movement_type"] for row in movements].count("IN") == 2
    assert [row["movement_type"] for row in movements].count("OUT") == 2
    assert all(
        row["animal_id"] == animal_id
        for row in movements
        if row["movement_type"] == "OUT"
    )


def test_expired_batches_are_not_usable_or_consumed(database):
    item_id = create_item(database, minimum=1)
    expired = (date.today() - timedelta(days=1)).isoformat()
    batch_id = receive(
        database,
        item_id,
        "B-EXPIRED",
        5,
        (date.today() + timedelta(days=1)).isoformat(),
    )
    with database.connection:
        database.connection.execute(
            "UPDATE inventory_batches SET expiry_date = ? WHERE id = ?",
            (expired, batch_id),
        )

    item = database.get_inventory_item(item_id)
    assert item["stock_quantity"] == 5
    assert item["usable_quantity"] == 0
    assert item["expired_quantity"] == 5
    assert item_id in {row["id"] for row in database.low_stock_items()}
    with pytest.raises(ValueError, match="Lô hết hạn"):
        database.consume_inventory_stock(item_id, {"quantity": 1})
    assert database.expiring_inventory_batches(30)[0]["batch_code"] == "B-EXPIRED"


def test_insufficient_stock_rolls_back_without_partial_deduction(database):
    item_id = create_item(database)
    receive(database, item_id, "B-1", 2, None)

    with pytest.raises(ValueError, match="không đủ"):
        database.consume_inventory_stock(item_id, {"quantity": 3})

    assert database.get_inventory_item(item_id)["usable_quantity"] == 2
    assert len(database.list_inventory_movements(item_id)) == 1


def test_inventory_rejects_duplicate_batches_and_invalid_values(database):
    item_id = create_item(database)
    receive(database, item_id, "B-1", 2, None)
    with pytest.raises(sqlite3.IntegrityError):
        receive(database, item_id, "B-1", 2, None)
    with pytest.raises(ValueError, match="lớn hơn 0"):
        database.consume_inventory_stock(item_id, {"quantity": 0})
    with pytest.raises(ValueError, match="hết hạn"):
        receive(database, item_id, "B-2", 2, "not-a-date")


def test_recommendation_profiles_are_validated_linked_and_audited(database):
    item_id = create_item(database)
    receive(database, item_id, "B-REC", 4, None)
    with pytest.raises(ValueError, match="khai báo loài"):
        database.save_recommendation_profile(
            item_id,
            {
                "recommendation_category": "FOOD",
                "species_tags": "",
            },
        )

    database.save_recommendation_profile(
        item_id,
        {
            "recommendation_category": "FOOD",
            "species_tags": "dog, cat",
            "age_groups": "young, adult",
            "breed_tags": "corgi",
            "gender_tags": "male",
            "needs_tags": "digestion",
            "recommendation_price": 250_000,
            "popularity": 75,
        },
    )
    products = database.list_recommendation_products()
    assert len(products) == 1
    assert products[0]["item_id"] == item_id
    assert products[0]["usable_quantity"] == 4
    profile = database.get_recommendation_profile(item_id)
    assert profile["recommendation_category"] == "FOOD"
    assert profile["recommendation_price"] == 250_000

    animal_id = database.save_animal(
        {
            "animal_code": "PET-REC-1",
            "name": "Mochi",
            "species": "Chó",
            "breed": "Corgi",
            "gender": "Đực",
            "birth_date": (date.today() - timedelta(days=180)).isoformat(),
        }
    )
    database.record_recommendation_interaction(animal_id, item_id, "PURCHASE")
    interactions = database.list_recommendation_interactions(animal_id)
    recommendations = recommend_products(
        [dict(products[0])],
        dict(database.get_animal(animal_id)),
        interactions,
        {"digestion"},
    )
    assert recommendations[0]["item_id"] == item_id
    assert recommendations[0]["score_breakdown"]["purchase_history"] > 50

    with pytest.raises(ValueError, match="không hợp lệ"):
        database.record_recommendation_interaction(animal_id, item_id, "FAKE_EVENT")


def test_pet_product_preferences_persist_and_change_recommendations(database):
    item_id = create_item(database)
    receive(database, item_id, "B-PREF", 4, None)
    database.save_recommendation_profile(
        item_id,
        {
            "recommendation_category": "FOOD",
            "species_tags": "dog",
            "recommendation_price": 200_000,
        },
    )
    animal_id = database.save_animal(
        {
            "animal_code": "PET-PREF-1",
            "name": "Mochi",
            "species": "Chó",
            "status": "AVAILABLE",
        }
    )
    pet = dict(database.get_animal(animal_id))
    products = [dict(database.list_recommendation_products()[0])]

    database.save_animal_product_preference(
        animal_id, item_id, "LIKE", "Đã được xác nhận"
    )
    preference = database.list_animal_product_preferences(animal_id)
    liked = recommend_products(products, pet, product_preferences=preference)

    assert preference[0]["preference"] == "LIKE"
    assert liked[0]["score_breakdown"]["behavior"] == 100
    assert "Đã lưu trong sở thích của bé" in liked[0]["reasons"]

    database.save_animal_product_preference(animal_id, item_id, "AVOID")
    avoided = recommend_products(
        products,
        pet,
        product_preferences=database.list_animal_product_preferences(animal_id),
    )
    assert avoided == []

    other_animal_id = database.save_animal(
        {
            "animal_code": "PET-PREF-2",
            "name": "Luna",
            "species": "Chó",
            "status": "AVAILABLE",
        }
    )
    assert database.list_animal_product_preferences(other_animal_id) == []
    assert recommend_products(products, dict(database.get_animal(other_animal_id)))

    database.delete_animal_product_preference(animal_id, item_id)
    assert database.list_animal_product_preferences(animal_id) == []
    assert recommend_products(products, pet)


def test_existing_inventory_items_migrate_for_grooming_and_accessories(tmp_path):
    database_path = tmp_path / "legacy_inventory.db"
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL CHECK (category IN ('FOOD', 'MEDICINE')),
            unit TEXT NOT NULL,
            minimum_stock REAL NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
            description TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE inventory_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
            batch_code TEXT NOT NULL,
            expiry_date TEXT,
            quantity_remaining REAL NOT NULL CHECK (quantity_remaining >= 0),
            unit_cost REAL NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
            received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (item_id, batch_code)
        );
        CREATE TABLE inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
            batch_id INTEGER NOT NULL REFERENCES inventory_batches(id) ON DELETE RESTRICT,
            movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
            quantity REAL NOT NULL CHECK (quantity > 0),
            occurred_on TEXT NOT NULL,
            animal_id INTEGER,
            reference TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO inventory_items (item_code, name, category, unit)
        VALUES ('LEGACY-FOOD', 'Thức ăn', 'FOOD', 'kg');
        INSERT INTO inventory_batches
            (item_id, batch_code, quantity_remaining, unit_cost)
        VALUES (1, 'B-OLD', 4, 100);
        INSERT INTO inventory_movements
            (item_id, batch_id, movement_type, quantity, occurred_on)
        VALUES (1, 1, 'IN', 4, '2026-09-01');
        """
    )
    connection.commit()
    connection.close()

    database = Database(database_path)
    try:
        assert database.get_inventory_item(1)["name"] == "Thức ăn"
        assert database.list_inventory_batches(1)[0]["quantity_remaining"] == 4
        assert database.list_inventory_movements(1)[0]["movement_type"] == "IN"
        assert database.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        supply_id = database.save_inventory_item(
            {
                "item_code": "BRUSH-01",
                "name": "Bàn chải",
                "category": "SUPPLIES",
                "unit": "cái",
                "minimum_stock": 0,
            }
        )
        assert database.get_inventory_item(supply_id)["category"] == "SUPPLIES"
    finally:
        database.close()
