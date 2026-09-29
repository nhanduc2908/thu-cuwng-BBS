from __future__ import annotations

import sqlite3
from typing import Any


def sanitize_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize feedback records before storing."""
    rating = int(payload.get("rating", 0))
    rating = max(0, min(5, rating))
    feedback = {
        "customer_id": payload.get("customer_id"),
        "pet_id": payload.get("pet_id"),
        "source": str(payload.get("source", "WEB")).upper(),
        "channel": str(payload.get("channel", "GENERAL")).upper(),
        "rating": rating,
        "title": str(payload.get("title", "")).strip()[:200],
        "message": str(payload.get("message", "")).strip()[:2000],
    }
    if feedback["source"] not in {"WEB", "APP", "STAFF", "CALL", "OTHER"}:
        feedback["source"] = "OTHER"
    if feedback["channel"] not in {"GENERAL", "SALE", "SERVICE", "HEALTH", "FEEDING", "OTHER"}:
        feedback["channel"] = "OTHER"
    return feedback


def record_feedback(
    payload: dict[str, Any],
    connection: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Persist customer feedback and return the stored record summary."""
    record = sanitize_feedback(payload)
    if connection is None:
        return {"stored": False, **record}

    cursor = connection.execute(
        """
        INSERT INTO customer_feedback (
            customer_id, pet_id, source, channel, rating, title, message
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["customer_id"],
            record["pet_id"],
            record["source"],
            record["channel"],
            record["rating"],
            record["title"],
            record["message"],
        ),
    )
    return {
        "stored": True,
        "id": int(cursor.lastrowid),
        **record,
    }


def aggregate_feedback(feedback_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute a compact quality signal for the feedback loop."""
    if not feedback_rows:
        return {"count": 0, "average_rating": 0.0, "positive_ratio": 0.0}

    ratings = [int(row.get("rating", 0)) for row in feedback_rows]
    positive = sum(1 for value in ratings if value >= 4)
    return {
        "count": len(ratings),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "positive_ratio": round(positive / len(ratings), 2),
    }
