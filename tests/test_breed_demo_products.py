import sqlite3

from app.database import Database
from app.storefront_catalog import build_storefront_catalog
from scripts.seed_breed_demo_products import (
    DEMO_NOTICE,
    FOOD_NOTICE,
    build_demo_products,
    insert_demo_products,
    load_breed_profiles,
)


def test_builds_exact_demo_mix_for_all_breeds_without_medicine_claims():
    breeds = load_breed_profiles()
    rows = build_demo_products(breeds)

    assert len(rows) == 10_000
    assert sum(row[2] == "FOOD" and row[9] in {"YOUNG", "ADULT", "SENIOR"} for row in rows) == 600
    assert sum(row[2] == "FOOD" and row[5] == "Thực phẩm bổ sung mẫu" for row in rows) == 4_700
    assert sum(row[2] == "SUPPLIES" for row in rows) == 4_700
    assert {row[8] for row in rows} == {breed["name"] for breed in breeds}
    assert all("MEDICINE" not in row[2] for row in rows)
    assert all("chưa xác minh" in row[4].casefold() for row in rows if row[2] == "SUPPLIES")
    assert "không đại diện công thức" in FOOD_NOTICE
    assert "không phải khuyến nghị" in DEMO_NOTICE


def test_insert_is_idempotent_and_creates_no_stock():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY,
            item_code TEXT UNIQUE,
            name TEXT,
            category TEXT,
            unit TEXT,
            minimum_stock REAL,
            description TEXT,
            catalog_category TEXT,
            target_species TEXT,
            age_group TEXT,
            brand TEXT,
            retail_price REAL,
            is_demo INTEGER,
            animal_subspecies TEXT,
            age_unit TEXT,
            life_stage TEXT,
            food_category TEXT,
            food_type TEXT,
            feeding_frequency TEXT,
            purpose TEXT
        )
        """
    )
    rows = build_demo_products(load_breed_profiles())

    assert insert_demo_products(connection, rows) == 10_000
    assert insert_demo_products(connection, rows) == 0
    assert connection.execute("SELECT COUNT(*) FROM inventory_items").fetchone()[0] == 10_000
    assert connection.execute("SELECT COUNT(*) FROM inventory_items WHERE is_demo != 1").fetchone()[0] == 0
    assert connection.execute("SELECT COUNT(*) FROM inventory_items WHERE retail_price != 0").fetchone()[0] == 0


def test_import_matches_the_real_application_schema_and_storefront_export(tmp_path):
    database = Database(tmp_path / "breed-products.db")
    try:
        rows = build_demo_products(load_breed_profiles())
        assert insert_demo_products(database.connection, rows) == 10_000
        catalog = build_storefront_catalog(database.connection)
        imported = [
            item for item in catalog["products"]
            if item["item_code"].startswith("DEMO-BREED-")
        ]

        assert len(imported) == 10_000
        assert all(item["is_demo"] and item["retail_price"] == 0 for item in imported)
        assert all(item["stock_quantity"] == 0 for item in imported)
        assert {item["animal_subspecies"] for item in imported} == {
            breed["name"] for breed in load_breed_profiles()
        }
        database.inventory.seed_feeding_profiles()
        supplement = database.connection.execute(
            """
            SELECT life_stage, age_min_months, age_max_months, food_type
            FROM inventory_items WHERE item_code = 'DEMO-BREED-DOG_GOLDEN_RETRIEVER-SUP-01'
            """
        ).fetchone()
        assert tuple(supplement) == ("", None, None, "Theo nhãn")
    finally:
        database.close()
