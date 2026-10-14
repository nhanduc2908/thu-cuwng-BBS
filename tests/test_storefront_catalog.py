import json
import sqlite3

from app.storefront_catalog import PUBLIC_ITEM_FIELDS, build_storefront_catalog
from app.database import Database
from app.web_bridge import LocalAdminBridge


def _catalog_connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    columns = ["id INTEGER PRIMARY KEY", "unit_cost REAL", "supplier_id INTEGER"]
    for field in PUBLIC_ITEM_FIELDS:
        if field not in {"item_code", "is_demo", "is_active"}:
            columns.append(f'"{field}"')
        else:
            columns.append(f'"{field}"')
    connection.execute(f"CREATE TABLE inventory_items ({', '.join(columns)})")
    connection.execute(
        """
        CREATE TABLE inventory_batches (
            item_id INTEGER, expiry_date TEXT, quantity_remaining REAL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE product_combos (
            id INTEGER PRIMARY KEY, combo_code TEXT, name TEXT, description TEXT,
            target_species TEXT, sale_price REAL, member_price REAL,
            promotion_percent REAL, is_demo INTEGER, is_active INTEGER
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE product_combo_items (
            combo_id INTEGER, item_id INTEGER, quantity REAL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE sales_orders (
            id INTEGER PRIMARY KEY, ordered_at TEXT, status TEXT,
            inventory_fulfilled_at TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE sales_product_items (
            order_id INTEGER, item_id INTEGER, combo_id INTEGER,
            quantity REAL, line_total REAL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE storefront_order_requests (
            items_json TEXT, created_at TEXT
        )
        """
    )
    item_fields = [field for field in PUBLIC_ITEM_FIELDS if field != "id"]
    values = {field: None for field in item_fields}
    values.update({
        "item_code": "SKU-1",
        "name": "Thức ăn chó demo",
        "category": "FOOD",
        "unit": "gói",
        "retail_price": 100000,
        "is_demo": 0,
        "is_active": 1,
        "catalog_category": "Thức ăn chó",
        "target_species": "Chó",
        "life_stage": "Trưởng thành",
    })
    names = list(values)
    placeholders = ", ".join("?" for _ in names)
    connection.execute(
        f'INSERT INTO inventory_items ({", ".join(names)}) VALUES ({placeholders})',
        [values[name] for name in names],
    )
    connection.execute(
        "INSERT INTO inventory_batches VALUES (1, '2099-01-01', 10)"
    )
    connection.execute(
        "INSERT INTO product_combos VALUES (1, 'COMBO-1', 'Combo demo', 'Mô tả', 'Chó', 200000, NULL, 0, 1, 1)"
    )
    connection.execute("INSERT INTO product_combo_items VALUES (1, 1, 2)")
    return connection


def test_storefront_catalog_exports_active_products_stock_and_combo_components_only():
    connection = _catalog_connection()
    try:
        catalog = build_storefront_catalog(connection)
    finally:
        connection.close()

    assert catalog["sourceType"] == "live_sqlite"
    assert catalog["summary"] == {
        "productCount": 1,
        "comboCount": 1,
        "demoProductCount": 0,
        "demoComboCount": 1,
        "inStockCount": 1,
        "outOfStockCount": 0,
    }
    product = catalog["products"][0]
    assert product["usable_quantity"] == 10
    assert "unit_cost" not in product
    assert "supplier_id" not in product
    combo = catalog["combos"][0]
    assert combo["stock_status"] == "in_stock"
    assert combo["components"][0]["usable_quantity"] == 10
    assert combo["usable_quantity"] == 5


def test_storefront_popularity_uses_paid_sales_and_separates_requests():
    from datetime import datetime, timedelta

    connection = _catalog_connection()
    now = datetime.now().isoformat(timespec="seconds")
    old_date = (datetime.now() - timedelta(days=45)).isoformat(timespec="seconds")
    connection.executemany(
        "INSERT INTO sales_orders VALUES (?, ?, ?, NULL)",
        [
            (1, now, "PAID"),
            (2, now, "PAID"),
            (3, now, "PARTIALLY_PAID"),
            (4, now, "CANCELLED"),
            (5, old_date, "PAID"),
        ],
    )
    connection.executemany(
        "INSERT INTO sales_product_items VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, None, 2, 200000),
            (2, 1, None, 1, 100000),
            (3, 1, None, 20, 2000000),
            (4, 1, None, 30, 3000000),
            (5, 1, None, 40, 4000000),
            (1, 1, 1, 2, 150000),
        ],
    )
    connection.executemany(
        "INSERT INTO storefront_order_requests VALUES (?, ?)",
        [
            (
                json.dumps([{"item_code": "SKU-1", "quantity": 3}]),
                now,
            ),
            (
                json.dumps([
                    {"item_code": "COMBO-1", "quantity": 1},
                    {"item_code": "COMBO-1", "quantity": 2},
                ]),
                now,
            ),
        ],
    )
    try:
        catalog = build_storefront_catalog(connection)
    finally:
        connection.close()

    product = catalog["products"][0]["popularity_30d"]
    combo = catalog["combos"][0]["popularity_30d"]
    assert product == {
        "sold_quantity": 3.0,
        "paid_order_count": 2,
        "revenue": 300000.0,
        "request_count": 1,
        "requested_quantity": 3.0,
        "score": 100.0,
    }
    assert combo["sold_quantity"] is None
    assert combo["paid_order_count"] == 1
    assert combo["request_count"] == 1
    assert combo["requested_quantity"] == 3.0
    assert 0 < combo["score"] < product["score"]
    assert catalog["popularity"]["periodDays"] == 30
    assert "customer_name" not in catalog
    assert "customer_phone" not in catalog
    assert "address" not in catalog


def test_public_storefront_bridge_serves_live_catalog_without_login(tmp_path):
    database_path = tmp_path / "storefront.db"
    database = Database(database_path)
    try:
        expected_count = sum(
            row["is_active"] for row in database.list_inventory_items()
        )
    finally:
        database.close()

    bridge = LocalAdminBridge(database_path, tmp_path, port=0)
    bridge.start()
    try:
        request = __import__("urllib.request", fromlist=["Request"]).Request(
            f"{bridge.base_url}/api/storefront/catalog"
        )
        with __import__("urllib.request", fromlist=["urlopen"]).urlopen(
            request, timeout=5
        ) as response:
            payload = json.loads(response.read())
        assert payload["sourceType"] == "live_sqlite"
        assert payload["summary"]["productCount"] == expected_count
        assert "customers" not in payload
        assert payload["popularity"]["periodDays"] == 30
        assert all("popularity_30d" in item for item in payload["products"])
        assert all("popularity_30d" in combo for combo in payload["combos"])
    finally:
        bridge.stop()
