import sqlite3
from datetime import date


class ReportRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def inventory(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT i.item_code, i.name, i.category, i.unit,
                   COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity,
                   i.minimum_stock, i.is_active
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.is_demo = 0 OR EXISTS (
                SELECT 1 FROM inventory_batches seeded_batch
                WHERE seeded_batch.item_id = i.id
            )
            GROUP BY i.id ORDER BY i.name COLLATE NOCASE
            """
        ).fetchall()

    def sales(self, start_date: str, end_date: str) -> list[sqlite3.Row]:
        self._validate_range(start_date, end_date)
        return self.connection.execute(
            """
            SELECT o.order_code, o.ordered_at, c.customer_code, c.name AS customer,
                   o.status, o.total_amount,
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             WHERE p.order_id = o.id), 0) AS paid_amount,
                   (SELECT COUNT(*) FROM order_items i
                    WHERE i.order_id = o.id)
                   + (SELECT COUNT(*) FROM sales_product_items pi
                      WHERE pi.order_id = o.id AND pi.combo_id IS NULL)
                   + (SELECT COUNT(DISTINCT pi.combo_id) FROM sales_product_items pi
                      WHERE pi.order_id = o.id AND pi.combo_id IS NOT NULL) AS item_count
            FROM sales_orders o
            JOIN customers c ON c.id = o.customer_id
            WHERE o.ordered_at BETWEEN ? AND ?
            ORDER BY o.ordered_at DESC, o.id DESC
            """,
            (start_date, end_date),
        ).fetchall()

    def health(self, start_date: str, end_date: str) -> list[sqlite3.Row]:
        self._validate_range(start_date, end_date)
        return self.connection.execute(
            """
            SELECT h.examination_date, a.animal_code, a.name AS animal_name,
                   a.species, h.health_status, h.diagnosis, h.treatment,
                   h.veterinarian, h.note
            FROM health_records h
            JOIN animals a ON a.id = h.animal_id
            WHERE h.examination_date BETWEEN ? AND ?
            ORDER BY h.examination_date DESC, h.id DESC
            """,
            (start_date, end_date),
        ).fetchall()

    @staticmethod
    def _validate_range(start_date: str, end_date: str) -> None:
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except (TypeError, ValueError) as error:
            raise ValueError("Khoảng thời gian báo cáo không hợp lệ.") from error
        if start > end:
            raise ValueError("Khoảng thời gian báo cáo không hợp lệ.")
