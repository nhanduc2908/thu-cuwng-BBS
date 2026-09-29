import sqlite3
from datetime import date
from typing import Any


class NotificationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_alerts(self) -> list[dict[str, Any]]:
        today = date.today().isoformat()
        alerts: list[dict[str, Any]] = []
        low_stock = self.connection.execute(
            """
            SELECT i.item_code, i.name, i.unit, i.minimum_stock,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.is_active = 1 AND (
                i.is_demo = 0 OR EXISTS (
                    SELECT 1 FROM inventory_batches seeded_batch
                    WHERE seeded_batch.item_id = i.id
                )
            )
            GROUP BY i.id
            HAVING usable_quantity <= i.minimum_stock
            """
        ).fetchall()
        for row in low_stock:
            alerts.append(
                {
                    "severity": "HIGH",
                    "category": "Tồn kho",
                    "title": f"Tồn thấp: {row['name']}",
                    "detail": (
                        f"{row['usable_quantity']:g} {row['unit']} còn dùng được; "
                        f"ngưỡng tối thiểu {row['minimum_stock']:g} {row['unit']}."
                    ),
                    "date": today,
                }
            )

        expiring = self.connection.execute(
            """
            SELECT i.name AS item_name, i.unit, b.batch_code, b.expiry_date,
                   b.quantity_remaining
            FROM inventory_batches b
            JOIN inventory_items i ON i.id = b.item_id
            WHERE i.is_active = 1 AND b.quantity_remaining > 0
              AND b.expiry_date IS NOT NULL
              AND b.expiry_date <= date('now', 'localtime', '+30 days')
            ORDER BY b.expiry_date
            """
        ).fetchall()
        for row in expiring:
            expired = row["expiry_date"] < today
            alerts.append(
                {
                    "severity": "HIGH" if expired else "MEDIUM",
                    "category": "Hạn sử dụng",
                    "title": (
                        f"Đã hết hạn: {row['item_name']}"
                        if expired
                        else f"Sắp hết hạn: {row['item_name']}"
                    ),
                    "detail": (
                        f"Lô {row['batch_code']}; hạn {row['expiry_date']}; "
                        f"còn {row['quantity_remaining']:g} {row['unit']}."
                    ),
                    "date": row["expiry_date"],
                }
            )

        care_tasks = self.connection.execute(
            """
            SELECT t.id, t.title, t.scheduled_at, a.animal_code, a.name AS animal_name
            FROM care_tasks t
            JOIN animals a ON a.id = t.animal_id
            WHERE t.is_completed = 0
              AND date(t.scheduled_at) <= date('now', 'localtime')
            ORDER BY t.scheduled_at
            """
        ).fetchall()
        for row in care_tasks:
            alerts.append(
                {
                    "severity": "MEDIUM",
                    "category": "Chăm sóc",
                    "title": f"Việc cần làm: {row['title']}",
                    "detail": (
                        f"{row['animal_code']} — {row['animal_name']}; "
                        f"lịch {row['scheduled_at']}."
                    ),
                    "date": row["scheduled_at"],
                }
            )

        expired_reservations = self.connection.execute(
            """
            SELECT r.id, r.expires_at, c.name AS customer_name,
                   a.animal_code, a.name AS animal_name
            FROM reservations r
            JOIN customers c ON c.id = r.customer_id
            JOIN animals a ON a.id = r.animal_id
            WHERE r.status = 'ACTIVE' AND r.expires_at < ?
            ORDER BY r.expires_at
            """,
            (today,),
        ).fetchall()
        for row in expired_reservations:
            alerts.append(
                {
                    "severity": "MEDIUM",
                    "category": "Giữ chỗ",
                    "title": f"Giữ chỗ quá hạn: {row['animal_code']}",
                    "detail": (
                        f"{row['animal_name']} — khách {row['customer_name']}; "
                        f"hết hạn {row['expires_at']}. Cần liên hệ và xử lý hoàn cọc."
                    ),
                    "date": row["expires_at"],
                }
            )

        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return sorted(
            alerts, key=lambda alert: (order[alert["severity"]], alert["date"])
        )
