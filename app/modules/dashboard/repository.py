import sqlite3

from app.modules.animals.constants import ANIMAL_STATUSES


class DashboardRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def dashboard_counts(self) -> dict[str, int]:
        rows = self.connection.execute(
            "SELECT status, COUNT(*) AS total FROM animals GROUP BY status"
        ).fetchall()
        counts = {status: 0 for status in ANIMAL_STATUSES}
        for row in rows:
            counts[row["status"]] = row["total"]
        counts["TOTAL"] = sum(counts.values())
        return counts

    def recent_animals(self, limit: int = 5) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT animal_code, name, species, status, created_at
            FROM animals ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
