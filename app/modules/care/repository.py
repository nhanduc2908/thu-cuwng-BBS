import sqlite3

from app.modules.care.constants import CARE_CHECKLIST_ITEMS, CARE_CHECKLIST_STATUSES


class CareRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_care_tasks(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT c.*, a.animal_code, a.name AS animal_name
            FROM care_tasks c
            JOIN animals a ON a.id = c.animal_id
            ORDER BY c.is_completed, c.scheduled_at, c.id DESC
            """
        ).fetchall()

    def add_care_task(self, values: dict[str, object]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO care_tasks (animal_id, title, scheduled_at, assigned_to, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    values["animal_id"],
                    values["title"],
                    values["scheduled_at"],
                    values["assigned_to"],
                    values["note"],
                ),
            )
            return int(cursor.lastrowid)

    def set_care_task_completed(self, task_id: int, completed: bool) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE care_tasks SET is_completed = ? WHERE id = ?",
                (int(completed), task_id),
            )

    def get_care_checklist(
        self, animal_id: int, checklist_date: str
    ) -> dict[str, sqlite3.Row]:
        rows = self.connection.execute(
            """
            SELECT * FROM care_checklists
            WHERE animal_id = ? AND checklist_date = ?
            """,
            (animal_id, checklist_date),
        ).fetchall()
        return {row["item_key"]: row for row in rows}

    def save_care_checklist(
        self,
        animal_id: int,
        checklist_date: str,
        checked_by: str,
        items: list[dict[str, str]],
    ) -> None:
        valid_keys = {key for key, _ in CARE_CHECKLIST_ITEMS}
        if any(
            item["item_key"] not in valid_keys
            or item["status"] not in CARE_CHECKLIST_STATUSES
            for item in items
        ):
            raise ValueError("Checklist chứa mục hoặc trạng thái không hợp lệ.")
        with self.connection:
            self.connection.executemany(
                """
                INSERT INTO care_checklists
                    (animal_id, checklist_date, item_key, status, note, checked_by)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(animal_id, checklist_date, item_key) DO UPDATE SET
                    status = excluded.status,
                    note = excluded.note,
                    checked_by = excluded.checked_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                [
                    (
                        animal_id,
                        checklist_date,
                        item["item_key"],
                        item["status"],
                        item["note"],
                        checked_by,
                    )
                    for item in items
                ],
            )
