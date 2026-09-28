import sqlite3
from typing import Any


class HealthRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_health_records(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT h.*, a.animal_code, a.name AS animal_name
            FROM health_records h
            JOIN animals a ON a.id = h.animal_id
            ORDER BY h.examination_date DESC, h.id DESC
            """
        ).fetchall()

    def add_health_record(self, values: dict[str, Any]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO health_records
                    (animal_id, examination_date, health_status, diagnosis,
                     treatment, veterinarian, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["animal_id"],
                    values["examination_date"],
                    values["health_status"],
                    values["diagnosis"],
                    values["treatment"],
                    values["veterinarian"],
                    values["note"],
                ),
            )
            self.connection.execute(
                """
                UPDATE animals SET health_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (values["health_status"], values["animal_id"]),
            )
            return int(cursor.lastrowid)
