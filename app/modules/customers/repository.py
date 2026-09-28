import sqlite3
from typing import Any


class CustomerRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_customers(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT c.*,
                (SELECT COUNT(*) FROM sales_orders o WHERE o.customer_id = c.id)
                    AS order_count,
                (SELECT COALESCE(SUM(o.total_amount), 0) FROM sales_orders o
                 WHERE o.customer_id = c.id AND o.status = 'PAID') AS paid_total
            FROM customers c
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ?
                   OR c.customer_code LIKE ?
            """
            parameters = (pattern, pattern, pattern, pattern)
        query += " ORDER BY c.name COLLATE NOCASE"
        return self.connection.execute(query, parameters).fetchall()

    def get_customer(self, customer_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()

    def save_customer(
        self, values: dict[str, Any], customer_id: int | None = None
    ) -> int:
        code = str(values["customer_code"]).strip()
        name = str(values["name"]).strip()
        if not code or not name:
            raise ValueError("Mã khách hàng và họ tên là bắt buộc.")
        fields = (
            code,
            name,
            str(values.get("phone", "")).strip(),
            str(values.get("email", "")).strip(),
            str(values.get("address", "")).strip(),
            str(values.get("note", "")).strip(),
        )
        with self.connection:
            if customer_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO customers
                        (customer_code, name, phone, email, address, note)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)
            self.connection.execute(
                """
                UPDATE customers SET customer_code = ?, name = ?, phone = ?,
                    email = ?, address = ?, note = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, customer_id),
            )
            return customer_id
