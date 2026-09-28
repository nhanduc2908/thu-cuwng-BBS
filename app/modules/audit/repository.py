import sqlite3
from typing import Any


class AuditRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def record(
        self,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        details: str = "",
    ) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO audit_logs
                    (actor_id, action, entity_type, entity_id, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (actor_id, action, entity_type, entity_id, details[:2000]),
            )
            return int(cursor.lastrowid)

    def list_events(
        self,
        limit: int = 500,
        actor_id: int | None = None,
        entity_type: str | None = None,
    ) -> list[sqlite3.Row]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if actor_id is not None:
            conditions.append("l.actor_id = ?")
            parameters.append(actor_id)
        if entity_type:
            conditions.append("l.entity_type = ?")
            parameters.append(entity_type)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        parameters.append(max(1, min(limit, 2000)))
        return self.connection.execute(
            f"""
            SELECT l.id, l.actor_id, u.username, u.display_name, l.action,
                   l.entity_type, l.entity_id, l.details, l.occurred_at
            FROM audit_logs l
            LEFT JOIN users u ON u.id = l.actor_id
            {where}
            ORDER BY l.id DESC LIMIT ?
            """,
            parameters,
        ).fetchall()
