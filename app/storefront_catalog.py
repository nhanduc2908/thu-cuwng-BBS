from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import sqlite3
from typing import Any


POPULARITY_METRICS = (
    ("sold_quantity", 0.45),
    ("paid_order_count", 0.30),
    ("revenue", 0.15),
    ("request_count", 0.10),
)

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


def _recent_popularity(connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """Aggregate public product-level signals for the last 30 days."""
    metrics: dict[str, dict[str, Any]] = {}
    active_item_codes = {
        row["item_code"]
        for row in connection.execute(
            "SELECT item_code FROM inventory_items WHERE is_active = 1"
        ).fetchall()
    }
    active_combo_codes = {
        row["combo_code"]
        for row in connection.execute(
            "SELECT combo_code FROM product_combos WHERE is_active = 1"
        ).fetchall()
    }
    active_codes = active_item_codes | active_combo_codes
    sales_rows = connection.execute(
        """
        WITH order_sales AS (
            SELECT CASE
                       WHEN spi.combo_id IS NULL THEN i.item_code
                       ELSE c.combo_code
                   END AS item_code,
                   so.id AS order_id,
                   CASE
                       WHEN spi.combo_id IS NULL THEN SUM(spi.quantity)
                       ELSE NULL
                   END AS sold_quantity,
                   SUM(spi.line_total) AS revenue
            FROM sales_product_items spi
            JOIN sales_orders so ON so.id = spi.order_id
            LEFT JOIN inventory_items i ON i.id = spi.item_id
            LEFT JOIN product_combos c ON c.id = spi.combo_id
            WHERE so.status = 'PAID'
              AND datetime(so.ordered_at) >= datetime('now', '-30 days')
            GROUP BY CASE
                         WHEN spi.combo_id IS NULL THEN i.item_code
                         ELSE c.combo_code
                     END,
                     so.id,
                     spi.combo_id
        )
        SELECT item_code,
               SUM(sold_quantity) AS sold_quantity,
               COUNT(DISTINCT order_id) AS paid_order_count,
               SUM(revenue) AS revenue
        FROM order_sales
        WHERE item_code IS NOT NULL
        GROUP BY item_code
        """
    ).fetchall()
    for row in sales_rows:
        if row["item_code"] not in active_codes:
            continue
        metrics[row["item_code"]] = {
            "sold_quantity": (
                float(row["sold_quantity"])
                if row["sold_quantity"] is not None
                else None
            ),
            "paid_order_count": int(row["paid_order_count"] or 0),
            "revenue": float(row["revenue"] or 0),
            "request_count": 0,
            "requested_quantity": 0.0,
        }

    request_rows = connection.execute(
        """
        SELECT items_json
        FROM storefront_order_requests
        WHERE datetime(created_at) >= datetime('now', '-30 days')
        """
    ).fetchall()
    for row in request_rows:
        items = json.loads(row["items_json"])
        if not isinstance(items, list):
            raise ValueError("Danh sách mặt hàng trong yêu cầu cửa hàng không hợp lệ.")
        seen_codes: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Mặt hàng trong yêu cầu cửa hàng không hợp lệ.")
            item_code = item.get("item_code")
            if not isinstance(item_code, str) or not item_code:
                raise ValueError("Mã mặt hàng trong yêu cầu cửa hàng không hợp lệ.")
            quantity = float(item.get("quantity", 0))
            if not math.isfinite(quantity) or quantity < 0:
                raise ValueError("Số lượng trong yêu cầu cửa hàng không hợp lệ.")
            if item_code not in active_codes:
                continue
            metric = metrics.setdefault(
                item_code,
                {
                    "sold_quantity": (
                        None if item_code in active_combo_codes else 0.0
                    ),
                    "paid_order_count": 0,
                    "revenue": 0.0,
                    "request_count": 0,
                    "requested_quantity": 0.0,
                },
            )
            metric["requested_quantity"] += quantity
            if item_code not in seen_codes:
                metric["request_count"] += 1
                seen_codes.add(item_code)

    maxima = {
        key: max(
            (
                math.log1p(float(metric[key]))
                for metric in metrics.values()
                if metric[key] is not None
            ),
            default=0.0,
        )
        for key, _weight in POPULARITY_METRICS
    }
    for metric in metrics.values():
        weighted_score = 0.0
        available_weight = 0.0
        for key, weight in POPULARITY_METRICS:
            if metric[key] is None:
                continue
            maximum = maxima[key]
            normalized = (
                math.log1p(float(metric[key])) / maximum
                if maximum > 0
                else 0.0
            )
            weighted_score += normalized * weight
            available_weight += weight
        metric["score"] = (
            round(weighted_score / available_weight * 100, 1)
            if available_weight > 0
            else 0.0
        )
        if metric["sold_quantity"] is not None:
            metric["sold_quantity"] = round(metric["sold_quantity"], 2)
        metric["revenue"] = round(metric["revenue"], 2)
        metric["requested_quantity"] = round(metric["requested_quantity"], 2)
    return metrics


def build_storefront_catalog(
    connection: sqlite3.Connection,
    source_type: str = "live_sqlite",
) -> dict[str, Any]:
    """Build a public, read-only catalog without internal costs or customer data."""
    popularity = _recent_popularity(connection)
    item_rows = connection.execute(
        """
        SELECT i.*,
               COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
               MAX(0, COALESCE(SUM(CASE
                   WHEN b.expiry_date IS NULL
                     OR b.expiry_date >= date('now', 'localtime')
                   THEN b.quantity_remaining ELSE 0 END), 0) - COALESCE((
                       SELECT SUM(pi.quantity)
                       FROM sales_product_items pi
                       JOIN sales_orders so ON so.id = pi.order_id
                       WHERE pi.item_id = i.id
                         AND so.status IN ('OPEN', 'PARTIALLY_PAID')
                         AND so.inventory_fulfilled_at IS NULL
                   ), 0)) AS usable_quantity
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
                "popularity_30d": popularity.get(
                    row["item_code"],
                    {
                        "sold_quantity": 0.0,
                        "paid_order_count": 0,
                        "revenue": 0.0,
                        "request_count": 0,
                        "requested_quantity": 0.0,
                        "score": 0.0,
                    },
                ),
                "stock_status": (
                    "in_stock"
                    if row["usable_quantity"] >= 5
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
            SELECT i.item_code, i.name, i.unit, ci.quantity, i.is_active,
                   MAX(0, COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) - COALESCE((
                           SELECT SUM(pi.quantity)
                           FROM sales_product_items pi
                           JOIN sales_orders so ON so.id = pi.order_id
                           WHERE pi.item_id = i.id
                             AND so.status IN ('OPEN', 'PARTIALLY_PAID')
                             AND so.inventory_fulfilled_at IS NULL
                       ), 0)) AS usable_quantity
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
        available_combo_quantity = min(
            (
                int(float(component["usable_quantity"]) // float(component["quantity"]))
                for component in components
                if component["is_active"] and float(component["quantity"]) > 0
            ),
            default=0,
        )
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
                "stock_quantity": available_combo_quantity,
                "usable_quantity": available_combo_quantity,
                "popularity_30d": popularity.get(
                    row["combo_code"],
                    {
                        "sold_quantity": None,
                        "paid_order_count": 0,
                        "revenue": 0.0,
                        "request_count": 0,
                        "requested_quantity": 0.0,
                        "score": 0.0,
                    },
                ),
                "stock_status": (
                    "in_stock"
                    if components
                    and all(
                        component["is_active"]
                        and component["usable_quantity"] >= component["quantity"] * 5
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
        "popularity": {
            "periodDays": 30,
            "weights": {
                "soldQuantity": 0.45,
                "paidOrderCount": 0.30,
                "revenue": 0.15,
                "requestCount": 0.10,
            },
            "basis": (
                "Điểm 0–100 chuẩn hóa theo logarit giữa các sản phẩm; chỉ tính "
                "đơn PAID trong 30 ngày. Yêu cầu mua được tính riêng, không phải "
                "doanh số. Số lượng combo không có trong dòng bán nên điểm combo "
                "được chuẩn hóa theo các tín hiệu đo được."
            ),
        },
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
            "inStockCount": sum(item["usable_quantity"] >= 5 for item in products),
            "outOfStockCount": sum(item["usable_quantity"] < 5 for item in products),
        },
        "products": products,
        "combos": combos,
    }
