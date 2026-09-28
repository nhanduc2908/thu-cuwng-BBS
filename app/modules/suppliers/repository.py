import sqlite3
from typing import Any


class SupplierRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_suppliers(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT s.*,
                (SELECT COUNT(*) FROM import_batches b WHERE b.supplier_id = s.id)
                    AS batch_count
            FROM suppliers s
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE s.supplier_code LIKE ? OR s.name LIKE ?
                   OR s.contact_person LIKE ? OR s.phone LIKE ?
            """
            parameters = (pattern, pattern, pattern, pattern)
        query += " ORDER BY s.is_active DESC, s.name COLLATE NOCASE"
        return self.connection.execute(query, parameters).fetchall()

    def get_supplier(self, supplier_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM suppliers WHERE id = ?", (supplier_id,)
        ).fetchone()

    def save_supplier(
        self, values: dict[str, Any], supplier_id: int | None = None
    ) -> int:
        code = str(values["supplier_code"]).strip()
        name = str(values["name"]).strip()
        if not code or not name:
            raise ValueError("Mã nhà cung cấp và tên nhà cung cấp là bắt buộc.")
        fields = (
            code,
            name,
            str(values.get("contact_person", "")).strip(),
            str(values.get("phone", "")).strip(),
            str(values.get("email", "")).strip(),
            str(values.get("address", "")).strip(),
            str(values.get("tax_code", "")).strip(),
            str(values.get("note", "")).strip(),
        )
        with self.connection:
            if supplier_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO suppliers
                        (supplier_code, name, contact_person, phone, email,
                         address, tax_code, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)
            self.connection.execute(
                """
                UPDATE suppliers SET
                    supplier_code = ?, name = ?, contact_person = ?, phone = ?,
                    email = ?, address = ?, tax_code = ?, note = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, supplier_id),
            )
            return supplier_id

    def set_supplier_active(self, supplier_id: int, active: bool) -> None:
        with self.connection:
            updated = self.connection.execute(
                """
                UPDATE suppliers SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (int(active), supplier_id),
            )
            if updated.rowcount != 1:
                raise ValueError("Không tìm thấy nhà cung cấp.")
