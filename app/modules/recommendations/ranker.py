from __future__ import annotations

from typing import Any


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a deterministic ranking from highest score to lowest."""
    return sorted(
        candidates,
        key=lambda item: (
            -float(item.get("score", 0)),
            float(item.get("recommendation_price", 0)),
            str(item.get("name", "")).casefold(),
        ),
    )
