import sqlite3
from typing import Any


UNAVAILABLE_ANIMAL_STATUSES = {"SOLD", "TRANSFERRED", "DECEASED"}


class StoreRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_cages(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT c.*,
                (SELECT COUNT(*) FROM animal_cage_assignments a
                 WHERE a.cage_id = c.id AND a.released_at IS NULL) AS assigned_count
            FROM cages c
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += " WHERE c.cage_code LIKE ? OR c.name LIKE ? OR c.area LIKE ?"
            parameters = (pattern, pattern, pattern)
        query += " ORDER BY c.is_active DESC, c.area, c.cage_code"
        return self.connection.execute(query, parameters).fetchall()

    def get_cage(self, cage_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT c.*,
                (SELECT COUNT(*) FROM animal_cage_assignments a
                 WHERE a.cage_id = c.id AND a.released_at IS NULL) AS assigned_count
            FROM cages c WHERE c.id = ?
            """,
            (cage_id,),
        ).fetchone()

    def save_cage(
        self, values: dict[str, Any], cage_id: int | None = None
    ) -> int:
        code = str(values["cage_code"]).strip()
        name = str(values["name"]).strip()
        capacity = int(values["capacity"])
        if not code or not name:
            raise ValueError("Mã chuồng và tên chuồng là bắt buộc.")
        if capacity < 1:
            raise ValueError("Sức chứa phải lớn hơn 0.")

        fields = (
            code,
            name,
            str(values.get("area", "")).strip(),
            str(values.get("accepted_species", "")).strip(),
            capacity,
            str(values.get("description", "")).strip(),
        )
        with self.connection:
            if cage_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO cages
                        (cage_code, name, area, accepted_species, capacity, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)

            current = self.connection.execute(
                "SELECT current_count FROM cages WHERE id = ?", (cage_id,)
            ).fetchone()
            if current is None:
                raise ValueError("Không tìm thấy chuồng cần cập nhật.")
            if capacity < current["current_count"]:
                raise ValueError(
                    f"Sức chứa mới không thể thấp hơn số động vật đang ở chuồng "
                    f"({current['current_count']})."
                )
            if values.get("accepted_species", "").strip():
                incompatible = self.connection.execute(
                    """
                    SELECT a.species
                    FROM animal_cage_assignments ca
                    JOIN animals a ON a.id = ca.animal_id
                    WHERE ca.cage_id = ? AND ca.released_at IS NULL
                      AND lower(a.species) != lower(?)
                    LIMIT 1
                    """,
                    (cage_id, values["accepted_species"].strip()),
                ).fetchone()
                if incompatible:
                    raise ValueError(
                        "Không thể giới hạn chuồng theo loài vì đang có động vật "
                        f"thuộc loài {incompatible['species']} trong chuồng."
                    )
            self.connection.execute(
                """
                UPDATE cages SET
                    cage_code = ?, name = ?, area = ?, accepted_species = ?,
                    capacity = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, cage_id),
            )
            return cage_id

    def delete_cage(self, cage_id: int) -> None:
        with self.connection:
            cage = self.connection.execute(
                """
                SELECT current_count,
                    EXISTS(
                        SELECT 1 FROM animal_cage_assignments a WHERE a.cage_id = cages.id
                    ) AS has_history
                FROM cages WHERE id = ?
                """,
                (cage_id,),
            ).fetchone()
            if cage is None:
                raise ValueError("Không tìm thấy chuồng cần xóa.")
            if cage["current_count"]:
                raise ValueError("Không thể xóa chuồng đang có động vật.")
            if cage["has_history"]:
                raise ValueError(
                    "Chuồng đã có lịch sử phân chuồng; hãy giữ lại để bảo toàn lịch sử."
                )
            self.connection.execute("DELETE FROM cages WHERE id = ?", (cage_id,))

    def set_cage_active(self, cage_id: int, active: bool) -> None:
        with self.connection:
            cage = self.connection.execute(
                "SELECT current_count FROM cages WHERE id = ?", (cage_id,)
            ).fetchone()
            if cage is None:
                raise ValueError("Không tìm thấy chuồng cần cập nhật.")
            if not active and cage["current_count"]:
                raise ValueError(
                    "Hãy chuyển động vật sang chuồng khác trước khi ngừng hoạt động."
                )
            self.connection.execute(
                """
                UPDATE cages SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (int(active), cage_id),
            )

    def list_cage_animals(self, cage_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT a.id, a.animal_code, a.name, a.species, a.status,
                   ca.assigned_at, ca.note
            FROM animal_cage_assignments ca
            JOIN animals a ON a.id = ca.animal_id
            WHERE ca.cage_id = ? AND ca.released_at IS NULL
            ORDER BY a.animal_code
            """,
            (cage_id,),
        ).fetchall()

    def list_cage_history(self, cage_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT a.animal_code, a.name AS animal_name, a.species,
                   ca.assigned_at, ca.released_at, ca.note
            FROM animal_cage_assignments ca
            JOIN animals a ON a.id = ca.animal_id
            WHERE ca.cage_id = ?
            ORDER BY ca.assigned_at DESC, ca.id DESC
            """,
            (cage_id,),
        ).fetchall()

    def assign_animal_to_cage(
        self, animal_id: int, cage_id: int, note: str = ""
    ) -> None:
        with self.connection:
            animal = self.connection.execute(
                "SELECT species, status FROM animals WHERE id = ?", (animal_id,)
            ).fetchone()
            if animal is None:
                raise ValueError("Không tìm thấy động vật cần phân chuồng.")
            if animal["status"] in UNAVAILABLE_ANIMAL_STATUSES:
                raise ValueError(
                    "Không thể xếp chuồng cho động vật đã bán, chuyển đi hoặc đã mất."
                )

            cage = self.connection.execute(
                "SELECT * FROM cages WHERE id = ?", (cage_id,)
            ).fetchone()
            if cage is None:
                raise ValueError("Không tìm thấy chuồng được chọn.")
            if not cage["is_active"]:
                raise ValueError("Chuồng đã ngừng hoạt động.")
            if (
                cage["accepted_species"]
                and cage["accepted_species"].casefold() != animal["species"].casefold()
            ):
                raise ValueError(
                    f"Chuồng này chỉ nhận loài {cage['accepted_species']}."
                )

            current = self.connection.execute(
                """
                SELECT id, cage_id FROM animal_cage_assignments
                WHERE animal_id = ? AND released_at IS NULL
                """,
                (animal_id,),
            ).fetchone()
            if current and current["cage_id"] == cage_id:
                return

            update = self.connection.execute(
                """
                UPDATE cages SET current_count = current_count + 1
                WHERE id = ? AND is_active = 1 AND current_count < capacity
                """,
                (cage_id,),
            )
            if update.rowcount != 1:
                raise ValueError("Chuồng đã đầy hoặc không còn hoạt động.")

            if current:
                self.connection.execute(
                    """
                    UPDATE animal_cage_assignments
                    SET released_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (current["id"],),
                )
                self.connection.execute(
                    """
                    UPDATE cages SET current_count = current_count - 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND current_count > 0
                    """,
                    (current["cage_id"],),
                )

            self.connection.execute(
                """
                INSERT INTO animal_cage_assignments (animal_id, cage_id, note)
                VALUES (?, ?, ?)
                """,
                (animal_id, cage_id, note.strip()),
            )
            self.connection.execute(
                """
                UPDATE animals SET cage_location = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (cage["name"], animal_id),
            )

    def unassign_animal_from_cage(self, animal_id: int) -> None:
        with self.connection:
            current = self.connection.execute(
                """
                SELECT id, cage_id FROM animal_cage_assignments
                WHERE animal_id = ? AND released_at IS NULL
                """,
                (animal_id,),
            ).fetchone()
            if current is None:
                raise ValueError("Động vật hiện chưa được xếp vào chuồng.")
            self.connection.execute(
                """
                UPDATE animal_cage_assignments
                SET released_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (current["id"],),
            )
            updated = self.connection.execute(
                """
                UPDATE cages SET current_count = current_count - 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND current_count > 0
                """,
                (current["cage_id"],),
            )
            if updated.rowcount != 1:
                raise sqlite3.IntegrityError("Số lượng động vật trong chuồng không nhất quán.")
            self.connection.execute(
                """
                UPDATE animals SET cage_location = '', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (animal_id,),
            )
