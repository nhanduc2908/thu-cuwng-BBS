from datetime import date, timedelta
import sqlite3

import pytest

from app.database import Database


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
