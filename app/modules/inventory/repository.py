import sqlite3
from datetime import date
import math
from typing import Any

from app.modules.inventory.constants import INVENTORY_CATEGORIES


class InventoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_items(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT i.*,
                   COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date < date('now', 'localtime')
                         AND b.quantity_remaining > 0
                       THEN b.quantity_remaining ELSE 0 END), 0) AS expired_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += " WHERE i.item_code LIKE ? OR i.name LIKE ?"
            parameters = (pattern, pattern)
        query += " GROUP BY i.id ORDER BY i.name COLLATE NOCASE"
        return self.connection.execute(query, parameters).fetchall()

    def get_item(self, item_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT i.*,
                   COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date < date('now', 'localtime')
                         AND b.quantity_remaining > 0
                       THEN b.quantity_remaining ELSE 0 END), 0) AS expired_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.id = ?
            GROUP BY i.id
            """,
            (item_id,),
        ).fetchone()

    def save_item(self, values: dict[str, Any], item_id: int | None = None) -> int:
        code = str(values.get("item_code", "")).strip()
        name = str(values.get("name", "")).strip()
        category = values.get("category")
        unit = str(values.get("unit", "")).strip()
        minimum = float(values.get("minimum_stock", 0))
        if not code or not name or not unit:
            raise ValueError("Mã, tên vật tư và đơn vị tính là bắt buộc.")
        if category not in INVENTORY_CATEGORIES:
            raise ValueError("Loại vật tư không hợp lệ.")
        if not math.isfinite(minimum) or minimum < 0:
            raise ValueError("Mức tồn tối thiểu không thể âm.")
        with self.connection:
            if item_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO inventory_items
                        (item_code, name, category, unit, minimum_stock, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        code,
                        name,
                        category,
                        unit,
                        minimum,
                        str(values.get("description", "")).strip(),
                    ),
                )
                return int(cursor.lastrowid)
            cursor = self.connection.execute(
                """
                UPDATE inventory_items SET item_code = ?, name = ?, category = ?,
                    unit = ?, minimum_stock = ?, description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    code,
                    name,
                    category,
                    unit,
                    minimum,
                    str(values.get("description", "")).strip(),
                    item_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError("Không tìm thấy vật tư.")
            return item_id

    def receive_stock(self, item_id: int, values: dict[str, Any]) -> int:
        batch_code = str(values.get("batch_code", "")).strip()
        quantity = float(values.get("quantity", 0))
        unit_cost = float(values.get("unit_cost", 0))
        expiry_date = values.get("expiry_date") or None
        if not batch_code:
            raise ValueError("Mã lô là bắt buộc.")
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("Số lượng nhập phải lớn hơn 0.")
        if not math.isfinite(unit_cost) or unit_cost < 0:
            raise ValueError("Giá nhập không thể âm.")
        if expiry_date:
            try:
                date.fromisoformat(expiry_date)
            except ValueError as error:
                raise ValueError("Ngày hết hạn không hợp lệ.") from error
            if expiry_date < date.today().isoformat():
                raise ValueError("Không thể nhập lô đã hết hạn.")
        with self.connection:
            item = self.connection.execute(
                "SELECT id FROM inventory_items WHERE id = ? AND is_active = 1",
                (item_id,),
            ).fetchone()
            if item is None:
                raise ValueError("Không tìm thấy vật tư đang hoạt động.")
            cursor = self.connection.execute(
                """
                INSERT INTO inventory_batches
                    (item_id, batch_code, expiry_date, quantity_remaining, unit_cost)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item_id, batch_code, expiry_date, quantity, unit_cost),
            )
            batch_id = int(cursor.lastrowid)
            self.connection.execute(
                """
                INSERT INTO inventory_movements
                    (item_id, batch_id, movement_type, quantity, occurred_on, reference, note)
                VALUES (?, ?, 'IN', ?, ?, ?, ?)
                """,
                (
                    item_id,
                    batch_id,
                    quantity,
                    values.get("occurred_on", date.today().isoformat()),
                    str(values.get("reference", "")).strip(),
                    str(values.get("note", "")).strip(),
                ),
            )
            return batch_id

    def consume_stock(self, item_id: int, values: dict[str, Any]) -> list[int]:
        quantity = float(values.get("quantity", 0))
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("Số lượng xuất dùng phải lớn hơn 0.")
        with self.connection:
            item = self.connection.execute(
                "SELECT id FROM inventory_items WHERE id = ? AND is_active = 1",
                (item_id,),
            ).fetchone()
            if item is None:
                raise ValueError("Không tìm thấy vật tư đang hoạt động.")
            batches = self.connection.execute(
                """
                SELECT id, quantity_remaining
                FROM inventory_batches
                WHERE item_id = ? AND quantity_remaining > 0
                  AND (
                      expiry_date IS NULL
                      OR expiry_date >= date('now', 'localtime')
                  )
                ORDER BY expiry_date IS NULL, expiry_date, id
                """,
                (item_id,),
            ).fetchall()
            usable = sum(float(batch["quantity_remaining"]) for batch in batches)
            if quantity > usable:
                raise ValueError(
                    f"Tồn kho dùng được không đủ (còn {usable:g}). "
                    "Lô hết hạn không được xuất dùng."
                )
            remaining = quantity
            movement_ids = []
            for batch in batches:
                if remaining <= 0:
                    break
                taken = min(remaining, float(batch["quantity_remaining"]))
                self.connection.execute(
                    """
                    UPDATE inventory_batches
                    SET quantity_remaining = quantity_remaining - ?
                    WHERE id = ?
                    """,
                    (taken, batch["id"]),
                )
                cursor = self.connection.execute(
                    """
                    INSERT INTO inventory_movements
                        (item_id, batch_id, movement_type, quantity, occurred_on,
                         animal_id, reference, note)
                    VALUES (?, ?, 'OUT', ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        batch["id"],
                        taken,
                        values.get("occurred_on", date.today().isoformat()),
                        values.get("animal_id"),
                        str(values.get("reference", "")).strip(),
                        str(values.get("note", "")).strip(),
                    ),
                )
                movement_ids.append(int(cursor.lastrowid))
                remaining = round(remaining - taken, 6)
            return movement_ids

    def list_batches(self, item_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM inventory_batches
            WHERE item_id = ? ORDER BY expiry_date IS NULL, expiry_date, id
            """,
            (item_id,),
        ).fetchall()

    def list_movements(self, item_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT m.*, b.batch_code, a.animal_code, a.name AS animal_name
            FROM inventory_movements m
            JOIN inventory_batches b ON b.id = m.batch_id
            LEFT JOIN animals a ON a.id = m.animal_id
            WHERE m.item_id = ?
            ORDER BY m.occurred_on DESC, m.id DESC
            """,
            (item_id,),
        ).fetchall()

    def low_stock_items(self) -> list[sqlite3.Row]:
        return [
            item
            for item in self.list_items()
            if item["is_active"]
            and item["usable_quantity"] <= item["minimum_stock"]
        ]

    def expiring_batches(self, days: int = 30) -> list[sqlite3.Row]:
        if days < 0:
            raise ValueError("Số ngày cảnh báo không thể âm.")
        return self.connection.execute(
            """
            SELECT b.*, i.item_code, i.name AS item_name, i.unit
            FROM inventory_batches b
            JOIN inventory_items i ON i.id = b.item_id
            WHERE i.is_active = 1 AND b.quantity_remaining > 0
              AND b.expiry_date IS NOT NULL
              AND b.expiry_date <= date('now', 'localtime', ?)
            ORDER BY b.expiry_date, i.name
            """,
            (f"+{days} days",),
        ).fetchall()

    def set_item_active(self, item_id: int, active: bool) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE inventory_items
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """,
                (int(active), item_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Không tìm thấy vật tư.")
