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

    def list_disease_catalog(self, species: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM disease_catalog WHERE is_active = 1"
        params: list[Any] = []
        if species is not None:
            query += " AND species = ?"
            params.append(species)
        query += " ORDER BY severity DESC, disease_name"
        return self.connection.execute(query, params).fetchall()

    def add_disease_catalog_entry(self, values: dict[str, Any]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO disease_catalog
                    (species, disease_code, disease_name, category, severity,
                     description, symptoms, treatment, prevention)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["species"],
                    values["disease_code"],
                    values["disease_name"],
                    values.get("category", "GENERAL"),
                    values.get("severity", "MEDIUM"),
                    values.get("description", ""),
                    values.get("symptoms", ""),
                    values.get("treatment", ""),
                    values.get("prevention", ""),
                ),
            )
            return int(cursor.lastrowid)

    def list_vaccination_schedules(self, species: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM vaccination_schedules WHERE is_active = 1"
        params: list[Any] = []
        if species is not None:
            query += " AND species = ?"
            params.append(species)
        query += " ORDER BY species, schedule_stage, vaccine_name"
        return self.connection.execute(query, params).fetchall()

    def add_vaccination_schedule(self, values: dict[str, Any]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO vaccination_schedules
                    (species, vaccine_name, schedule_stage, recommended_months,
                     dose_count, booster_interval_months, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["species"],
                    values["vaccine_name"],
                    values.get("schedule_stage", "PUPPY"),
                    values.get("recommended_months", "0-12"),
                    int(values.get("dose_count", 1)),
                    int(values.get("booster_interval_months", 12)),
                    values.get("notes", ""),
                ),
            )
            return int(cursor.lastrowid)

    def list_vaccination_records(self, animal_id: int | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM vaccination_records"
        params: list[Any] = []
        if animal_id is not None:
            query += " WHERE animal_id = ?"
            params.append(animal_id)
        query += " ORDER BY administered_at DESC, id DESC"
        return self.connection.execute(query, params).fetchall()

    def add_vaccination_record(self, values: dict[str, Any]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO vaccination_records
                    (animal_id, vaccine_name, administered_at, next_due_at, dose_number, veterinarian, note, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["animal_id"],
                    values["vaccine_name"],
                    values["administered_at"],
                    values.get("next_due_at", ""),
                    int(values.get("dose_number", 1)),
                    values.get("veterinarian", ""),
                    values.get("note", ""),
                    values.get("status", "COMPLETED"),
                ),
            )
            self.connection.execute(
                """
                UPDATE animals SET vaccination_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (values["vaccine_name"], values["animal_id"]),
            )
            return int(cursor.lastrowid)

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
