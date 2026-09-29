import sqlite3
from typing import Any

from app.modules.animals.constants import ANIMAL_PROFILE_FIELDS


class AnimalRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_animals(
        self, search: str = "", status: str | None = None
    ) -> list[sqlite3.Row]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if search.strip():
            pattern = f"%{search.strip()}%"
            conditions.append(
                "(a.animal_code LIKE ? OR a.name LIKE ? OR a.species LIKE ? OR a.breed LIKE ?)"
            )
            parameters.extend((pattern, pattern, pattern, pattern))
        if status:
            conditions.append("a.status = ?")
            parameters.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return self.connection.execute(
            f"""
            SELECT a.*, r.received_at, r.received_by
            FROM animals a
            LEFT JOIN animal_intake_receipts r ON r.animal_id = a.id
            {where_clause}
            ORDER BY a.id DESC
            """,
            parameters,
        ).fetchall()

    def get_animal(self, animal_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT a.*, r.received_at, r.received_by
            FROM animals a
            LEFT JOIN animal_intake_receipts r ON r.animal_id = a.id
            WHERE a.id = ?
            """,
            (animal_id,),
        ).fetchone()

    def save_animal(self, values: dict[str, Any], animal_id: int | None = None) -> int:
        fields = ANIMAL_PROFILE_FIELDS
        defaults = {
            "breed": "",
            "gender": "Chưa rõ",
            "birth_date": "",
            "color": "",
            "weight": None,
            "origin": "",
            "purchase_price": 0,
            "sale_price": 0,
            "status": "PENDING_INSPECTION",
            "health_status": "Bình thường",
            "description": "",
            "supplier_name": "",
            "intake_date": "",
            "microchip_id": "",
            "cage_location": "",
            "diet": "",
            "feeding_schedule": "",
            "allergies": "",
            "vaccination_status": "",
            "last_vet_visit": "",
            "exercise_needs": "",
            "behavior": "",
        }
        data = [
            values[field] if field in values else defaults[field]
            for field in fields
        ]
        with self.connection:
            if animal_id is None:
                placeholders = ", ".join("?" for _ in fields)
                cursor = self.connection.execute(
                    f"INSERT INTO animals ({', '.join(fields)}) VALUES ({placeholders})",
                    data,
                )
                return int(cursor.lastrowid)

            active_cage = self.connection.execute(
                """
                SELECT c.name, c.accepted_species
                FROM animal_cage_assignments a
                JOIN cages c ON c.id = a.cage_id
                WHERE a.animal_id = ? AND a.released_at IS NULL
                """,
                (animal_id,),
            ).fetchone()
            if active_cage:
                if (
                    active_cage["accepted_species"]
                    and active_cage["accepted_species"].casefold()
                    != str(values["species"]).strip().casefold()
                ):
                    raise ValueError(
                        "Không thể đổi loài vì động vật đang ở chuồng chỉ nhận "
                        f"{active_cage['accepted_species']}."
                    )
                data[fields.index("cage_location")] = active_cage["name"]

            assignments = ", ".join(f"{field} = ?" for field in fields)
            self.connection.execute(
                f"""
                UPDATE animals SET {assignments}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*data, animal_id),
            )
            return animal_id

    def delete_animal(self, animal_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM animals WHERE id = ?", (animal_id,))
