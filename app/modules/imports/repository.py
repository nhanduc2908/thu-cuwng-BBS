import sqlite3
from typing import Any

from app.modules.imports.constants import INSPECTION_RESULTS


ANIMAL_STATUS_BY_INSPECTION = {
    "PASSED": ("AVAILABLE", "Bình thường"),
    "QUARANTINE": ("QUARANTINE", "Theo dõi"),
    "NEEDS_TREATMENT": ("TREATMENT", "Đang điều trị"),
}


class ImportRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_batches(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT b.*, s.supplier_code, s.name AS supplier_name,
                (SELECT COUNT(*) FROM import_batch_animals ba
                 WHERE ba.batch_id = b.id) AS animal_count,
                (SELECT COUNT(DISTINCT i.animal_id)
                 FROM inspections i
                 JOIN import_batch_animals ba ON ba.animal_id = i.animal_id
                 WHERE ba.batch_id = b.id) AS inspected_count
            FROM import_batches b
            JOIN suppliers s ON s.id = b.supplier_id
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE b.batch_code LIKE ? OR s.name LIKE ? OR s.supplier_code LIKE ?
            """
            parameters = (pattern, pattern, pattern)
        query += " ORDER BY b.import_date DESC, b.id DESC"
        return self.connection.execute(query, parameters).fetchall()

    def create_batch(self, values: dict[str, Any]) -> int:
        code = str(values["batch_code"]).strip()
        if not code:
            raise ValueError("Mã lô nhập là bắt buộc.")
        with self.connection:
            supplier = self.connection.execute(
                "SELECT is_active FROM suppliers WHERE id = ?",
                (values["supplier_id"],),
            ).fetchone()
            if supplier is None:
                raise ValueError("Không tìm thấy nhà cung cấp.")
            if not supplier["is_active"]:
                raise ValueError("Không thể tạo lô nhập từ nhà cung cấp đã ngừng hoạt động.")
            cursor = self.connection.execute(
                """
                INSERT INTO import_batches
                    (batch_code, supplier_id, import_date, note)
                VALUES (?, ?, ?, ?)
                """,
                (
                    code,
                    values["supplier_id"],
                    values["import_date"],
                    str(values.get("note", "")).strip(),
                ),
            )
            return int(cursor.lastrowid)

    def list_batch_animals(self, batch_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT a.id, a.animal_code, a.name, a.species, a.breed,
                   a.purchase_price, a.status,
                   r.received_at, r.received_by,
                   (r.animal_id IS NOT NULL) AS receipt_confirmed,
                   i.result AS inspection_result,
                   i.inspected_at,
                   i.checked_by
            FROM import_batch_animals ba
            JOIN animals a ON a.id = ba.animal_id
            LEFT JOIN animal_intake_receipts r ON r.animal_id = a.id
            LEFT JOIN inspections i ON i.id = (
                SELECT latest.id FROM inspections latest
                WHERE latest.animal_id = a.id AND latest.batch_id = ba.batch_id
                ORDER BY latest.id DESC LIMIT 1
            )
            WHERE ba.batch_id = ?
            ORDER BY a.animal_code
            """,
            (batch_id,),
        ).fetchall()

    def add_animal_to_batch(
        self, batch_id: int, values: dict[str, Any]
    ) -> int:
        required = ("animal_code", "name", "species")
        if any(not str(values.get(field, "")).strip() for field in required):
            raise ValueError("Mã, tên và loài động vật là bắt buộc.")
        with self.connection:
            batch = self.connection.execute(
                """
                SELECT b.status, b.import_date, s.name AS supplier_name
                FROM import_batches b
                JOIN suppliers s ON s.id = b.supplier_id
                WHERE b.id = ?
                """,
                (batch_id,),
            ).fetchone()
            if batch is None:
                raise ValueError("Không tìm thấy lô nhập.")
            if batch["status"] != "OPEN":
                raise ValueError("Chỉ có thể thêm động vật vào lô đang tiếp nhận.")
            photo_data = values.get("photo_data")
            if not isinstance(photo_data, bytes) or not photo_data:
                raise ValueError("Cần đính kèm ảnh xác nhận bé đã được tiếp nhận.")
            if len(photo_data) > 8 * 1024 * 1024:
                raise ValueError("Ảnh tiếp nhận vượt quá giới hạn 8 MB.")
            photo_mime = str(values.get("photo_mime", "")).strip().lower()
            if photo_mime not in {"image/jpeg", "image/png", "image/webp"}:
                raise ValueError("Định dạng ảnh tiếp nhận không được hỗ trợ.")
            signatures = {
                "image/jpeg": photo_data.startswith(b"\xff\xd8\xff"),
                "image/png": photo_data.startswith(b"\x89PNG\r\n\x1a\n"),
                "image/webp": (
                    photo_data.startswith(b"RIFF")
                    and photo_data[8:12] == b"WEBP"
                ),
            }
            if not signatures[photo_mime]:
                raise ValueError("Nội dung ảnh không khớp với định dạng đã chọn.")
            received_by = str(values.get("received_by", "")).strip()
            confirmation = str(values.get("confirmation", "")).strip()
            if not received_by:
                raise ValueError("Cần ghi nhận nhân viên tiếp nhận.")
            if not confirmation:
                raise ValueError(
                    "Cần xác nhận bé đã được bàn giao và có mặt tại cửa hàng."
                )
            cursor = self.connection.execute(
                """
                INSERT INTO animals
                    (animal_code, name, species, breed, gender, birth_date,
                     origin, purchase_price, sale_price, status, supplier_name,
                     intake_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_INSPECTION', ?, ?, ?)
                """,
                (
                    str(values["animal_code"]).strip(),
                    str(values["name"]).strip(),
                    str(values["species"]).strip(),
                    str(values.get("breed", "")).strip(),
                    str(values.get("gender", "Chưa rõ")).strip(),
                    str(values.get("birth_date", "")).strip(),
                    str(values.get("origin", "")).strip(),
                    float(values.get("purchase_price", 0)),
                    float(values.get("sale_price", 0)),
                    batch["supplier_name"],
                    batch["import_date"],
                    str(values.get("description", "")).strip(),
                ),
            )
            animal_id = int(cursor.lastrowid)
            self.connection.execute(
                """
                INSERT INTO import_batch_animals (batch_id, animal_id, cost)
                VALUES (?, ?, ?)
                """,
                (batch_id, animal_id, float(values.get("purchase_price", 0))),
            )
            self.connection.execute(
                """
                INSERT INTO animal_intake_receipts
                    (animal_id, received_by, photo_mime, photo_data, confirmation)
                VALUES (?, ?, ?, ?, ?)
                """,
                (animal_id, received_by, photo_mime, photo_data, confirmation),
            )
            return animal_id

    def record_inspection(self, batch_id: int, values: dict[str, Any]) -> int:
        result = values["result"]
        if result not in INSPECTION_RESULTS:
            raise ValueError("Kết quả kiểm tra đầu vào không hợp lệ.")
        with self.connection:
            batch = self.connection.execute(
                "SELECT status FROM import_batches WHERE id = ?", (batch_id,)
            ).fetchone()
            if batch is None:
                raise ValueError("Không tìm thấy lô nhập.")
            if batch["status"] == "CANCELLED":
                raise ValueError("Không thể kiểm tra lô nhập đã hủy.")
            item = self.connection.execute(
                """
                SELECT a.id, a.status
                FROM import_batch_animals ba
                JOIN animals a ON a.id = ba.animal_id
                WHERE ba.batch_id = ? AND ba.animal_id = ?
                """,
                (batch_id, values["animal_id"]),
            ).fetchone()
            if item is None:
                raise ValueError("Động vật không thuộc lô nhập đã chọn.")
            if item["status"] in {"SOLD", "TRANSFERRED", "DECEASED"}:
                raise ValueError("Không thể kiểm tra động vật đã bán, chuyển đi hoặc đã mất.")
            cursor = self.connection.execute(
                """
                INSERT INTO inspections
                    (batch_id, animal_id, inspected_at, result, symptoms,
                     checked_by, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    values["animal_id"],
                    values["inspected_at"],
                    result,
                    str(values.get("symptoms", "")).strip(),
                    str(values.get("checked_by", "")).strip(),
                    str(values.get("note", "")).strip(),
                ),
            )
            animal_status, health_status = ANIMAL_STATUS_BY_INSPECTION[result]
            self.connection.execute(
                """
                UPDATE animals SET status = ?, health_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (animal_status, health_status, values["animal_id"]),
            )
            outstanding = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM import_batch_animals ba
                WHERE ba.batch_id = ?
                  AND NOT EXISTS (
                      SELECT 1 FROM inspections i
                      WHERE i.batch_id = ba.batch_id AND i.animal_id = ba.animal_id
                  )
                """,
                (batch_id,),
            ).fetchone()[0]
            total = self.connection.execute(
                "SELECT COUNT(*) FROM import_batch_animals WHERE batch_id = ?",
                (batch_id,),
            ).fetchone()[0]
            if total and outstanding == 0 and batch["status"] == "OPEN":
                self.connection.execute(
                    """
                    UPDATE import_batches SET status = 'COMPLETED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (batch_id,),
                )
            return int(cursor.lastrowid)

    def list_inspections(
        self, batch_id: int, animal_id: int | None = None
    ) -> list[sqlite3.Row]:
        query = """
            SELECT i.*, a.animal_code, a.name AS animal_name
            FROM inspections i
            JOIN animals a ON a.id = i.animal_id
            WHERE i.batch_id = ?
        """
        parameters: tuple[int, ...] = (batch_id,)
        if animal_id is not None:
            query += " AND i.animal_id = ?"
            parameters = (batch_id, animal_id)
        query += " ORDER BY i.inspected_at DESC, i.id DESC"
        return self.connection.execute(query, parameters).fetchall()

    def cancel_empty_batch(self, batch_id: int) -> None:
        with self.connection:
            batch = self.connection.execute(
                "SELECT status FROM import_batches WHERE id = ?", (batch_id,)
            ).fetchone()
            if batch is None:
                raise ValueError("Không tìm thấy lô nhập.")
            if batch["status"] != "OPEN":
                raise ValueError("Chỉ có thể hủy lô đang tiếp nhận.")
            count = self.connection.execute(
                "SELECT COUNT(*) FROM import_batch_animals WHERE batch_id = ?",
                (batch_id,),
            ).fetchone()[0]
            if count:
                raise ValueError(
                    "Lô đã có động vật; hãy giữ lại lịch sử và xử lý từng hồ sơ."
                )
            self.connection.execute(
                """
                UPDATE import_batches SET status = 'CANCELLED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (batch_id,),
            )
