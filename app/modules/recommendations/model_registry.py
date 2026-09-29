from __future__ import annotations

import sqlite3
from typing import Any


def register_model(
    model_name: str,
    metrics: dict[str, Any],
    version: str = "v1",
    status: str = "DRAFT",
    notes: str = "",
    connection: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Persist a model version in the registry and return a normalized record."""
    record = {
        "model_name": model_name,
        "version": version,
        "status": status.upper(),
        "metrics": metrics,
        "notes": notes,
    }
    if connection is None:
        return {"registered": False, **record}

    cursor = connection.execute(
        """
        INSERT INTO recommendation_model_registry (
            model_name, version, status, metric_snapshot, notes
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            model_name,
            version,
            record["status"],
            str(metrics),
            notes,
        ),
    )
    record["id"] = int(cursor.lastrowid)
    record["registered"] = True
    return record


def list_registered_models(connection: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    if connection is None:
        return []
    rows = connection.execute(
        "SELECT id, model_name, version, status, metric_snapshot, notes, created_at FROM recommendation_model_registry ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def latest_model(model_name: str, connection: sqlite3.Connection | None = None) -> dict[str, Any] | None:
    if connection is None:
        return None
    row = connection.execute(
        "SELECT id, model_name, version, status, metric_snapshot, notes, created_at FROM recommendation_model_registry WHERE model_name = ? ORDER BY created_at DESC LIMIT 1",
        (model_name,),
    ).fetchone()
    return dict(row) if row else None
