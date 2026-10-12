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
        "INSERT INTO inventory_batches VALUES (1, '2099-01-01', 5)"
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
    assert product["usable_quantity"] == 5
    assert "unit_cost" not in product
    assert "supplier_id" not in product
    combo = catalog["combos"][0]
    assert combo["stock_status"] == "in_stock"
    assert combo["components"][0]["usable_quantity"] == 5


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
    finally:
        bridge.stop()
