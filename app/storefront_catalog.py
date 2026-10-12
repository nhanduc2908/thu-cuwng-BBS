from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from typing import Any


PUBLIC_ITEM_FIELDS = (
    "item_code",
    "name",
    "category",
    "unit",
    "description",
    "catalog_category",
    "target_species",
    "age_group",
    "pack_size",
    "brand",
    "barcode",
    "retail_price",
    "member_price",
    "promotion_percent",
    "promotion_note",
    "ingredients",
    "image_path",
    "is_demo",
    "animal_subspecies",
    "age_min_months",
    "age_max_months",
    "age_unit",
    "life_stage",
    "food_category",
    "food_type",
    "food_subtype",
    "breed_size",
    "suitable_weight_min",
    "suitable_weight_max",
    "feeding_frequency",
    "feeding_time",
    "serving_size",
    "protein_source",
    "nutrition_type",
    "purpose",
    "vitamin_c_content",
    "water_level",
    "diet_type",
    "is_active",
)


def build_storefront_catalog(
    connection: sqlite3.Connection,
    source_type: str = "live_sqlite",
) -> dict[str, Any]:
    """Build a public, read-only catalog without internal costs or customer data."""
    item_rows = connection.execute(
        """
        SELECT i.*,
               COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
               COALESCE(SUM(CASE
                   WHEN b.expiry_date IS NULL
                     OR b.expiry_date >= date('now', 'localtime')
                   THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
        FROM inventory_items i
        LEFT JOIN inventory_batches b ON b.item_id = i.id
        WHERE i.is_active = 1
        GROUP BY i.id
        ORDER BY i.name COLLATE NOCASE, i.item_code COLLATE NOCASE
        """
    ).fetchall()
    products = []
    for row in item_rows:
        item = {field: row[field] for field in PUBLIC_ITEM_FIELDS}
        item.update(
            {
                "id": row["item_code"],
                "type": "inventory_item",
                "stock_quantity": row["stock_quantity"],
                "usable_quantity": row["usable_quantity"],
                "stock_status": (
                    "in_stock"
                    if row["usable_quantity"] > 0
                    else "out_of_stock"
                ),
            }
        )
        products.append(item)

    combo_rows = connection.execute(
        """
        SELECT c.combo_code, c.name, c.description, c.target_species,
               c.sale_price, c.member_price, c.promotion_percent,
               c.is_demo, c.is_active
        FROM product_combos c
        WHERE c.is_active = 1
        ORDER BY c.name COLLATE NOCASE, c.combo_code COLLATE NOCASE
        """
    ).fetchall()
    combos = []
    for row in combo_rows:
        component_rows = connection.execute(
            """
            SELECT i.item_code, i.name, i.unit, ci.quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
            FROM product_combo_items ci
            JOIN inventory_items i ON i.id = ci.item_id
            LEFT JOIN inventory_batches b ON b.item_id = ci.item_id
            WHERE ci.combo_id = (
                SELECT id FROM product_combos WHERE combo_code = ?
            )
            GROUP BY ci.item_id
            ORDER BY i.name COLLATE NOCASE, i.item_code COLLATE NOCASE
            """,
            (row["combo_code"],),
        ).fetchall()
        components = [dict(component) for component in component_rows]
        combos.append(
            {
                "id": row["combo_code"],
                "item_code": row["combo_code"],
                "name": row["name"],
                "category": "COMBO",
                "catalog_category": "Combo",
                "target_species": row["target_species"],
                "unit": "combo",
                "description": row["description"],
                "retail_price": row["sale_price"],
                "member_price": row["member_price"],
                "promotion_percent": row["promotion_percent"],
                "is_demo": row["is_demo"],
                "is_active": row["is_active"],
                "type": "combo",
                "components": components,
                "stock_status": (
                    "in_stock"
                    if components
                    and all(
                        component["usable_quantity"] >= component["quantity"]
                        for component in components
                    )
                    else "out_of_stock"
                ),
            }
        )

    return {
        "catalogVersion": 2,
        "source": "PetCare SQLite inventory_items and product_combos",
        "sourceType": source_type,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataStatus": (
            "demo_only"
            if all(bool(item["is_demo"]) for item in products + combos)
            else "mixed_demo_and_operational"
        ),
        "notice": (
            "Catalog đồng bộ từ cơ sở dữ liệu ứng dụng PetCare. Bản ghi demo cần "
            "xác nhận trước khi bán; tồn khả dụng được tính từ các lô chưa hết hạn. "
            "Không bao gồm giá vốn, nhà cung cấp, mã lô hoặc dữ liệu khách hàng."
        ),
        "summary": {
            "productCount": len(products),
            "comboCount": len(combos),
            "demoProductCount": sum(bool(item["is_demo"]) for item in products),
            "demoComboCount": sum(bool(combo["is_demo"]) for combo in combos),
            "inStockCount": sum(item["usable_quantity"] > 0 for item in products),
            "outOfStockCount": sum(item["usable_quantity"] <= 0 for item in products),
        },
        "products": products,
        "combos": combos,
    }
