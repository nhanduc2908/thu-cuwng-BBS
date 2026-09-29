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

    def list_pets(self, customer_id: int | None = None) -> list[sqlite3.Row]:
        if customer_id is None:
            return self.connection.execute(
                "SELECT * FROM pet_profiles ORDER BY created_at DESC"
            ).fetchall()
        return self.connection.execute(
            "SELECT * FROM pet_profiles WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,),
        ).fetchall()

    def get_pet(self, pet_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM pet_profiles WHERE id = ?",
            (pet_id,),
        ).fetchone()

    def save_pet(
        self, values: dict[str, Any], pet_id: int | None = None
    ) -> int:
        required_fields = ["customer_id", "name", "species"]
        for field in required_fields:
            if field not in values or str(values[field]).strip() == "":
                raise ValueError(f"Trường {field} là bắt buộc.")

        payload = (
            int(values["customer_id"]),
            str(values["name"]).strip(),
            str(values.get("species", "Chó")).strip(),
            str(values.get("breed_name", "")).strip(),
            values.get("breed_profile_id"),
            str(values.get("birth_date", "")).strip(),
            str(values.get("sex", "Chưa rõ")).strip(),
            str(values.get("color", "")).strip(),
            values.get("weight_kg"),
            str(values.get("activity_level", "Trung bình")).strip(),
            str(values.get("environment_type", "Trong nhà")).strip(),
            str(values.get("body_condition", "Bình thường")).strip(),
            str(values.get("health_status", "Bình thường")).strip(),
            str(values.get("microchip_id", "")).strip(),
            str(values.get("notes", "")).strip(),
        )

        with self.connection:
            if pet_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO pet_profiles (
                        customer_id, name, species, breed_name, breed_profile_id, birth_date,
                        sex, color, weight_kg, activity_level, environment_type,
                        body_condition, health_status, microchip_id, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    payload,
                )
                return int(cursor.lastrowid)

            self.connection.execute(
                """
                UPDATE pet_profiles SET
                    customer_id = ?, name = ?, species = ?, breed_name = ?, breed_profile_id = ?,
                    birth_date = ?, sex = ?, color = ?, weight_kg = ?, activity_level = ?,
                    environment_type = ?, body_condition = ?, health_status = ?,
                    microchip_id = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*payload, pet_id),
            )
            return pet_id
