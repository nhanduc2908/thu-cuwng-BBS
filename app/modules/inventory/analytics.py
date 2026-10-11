from collections.abc import Iterable, Mapping
from typing import Any


def summarize_categories(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for row in rows:
        category = str(row["category"])
        summary = summaries.setdefault(
            category,
            {
                "category": category,
                "item_count": 0,
                "stock_quantity": 0.0,
                "usable_quantity": 0.0,
                "expired_quantity": 0.0,
                "stock_value": 0.0,
            },
        )
        summary["item_count"] += 1
        summary["stock_quantity"] += float(row["stock_quantity"] or 0)
        summary["usable_quantity"] += float(row["usable_quantity"] or 0)
        summary["expired_quantity"] += float(row["expired_quantity"] or 0)
        summary["stock_value"] += float(row["stock_value"] or 0)
    return [
        {
            **summary,
            "stock_quantity": round(summary["stock_quantity"], 6),
            "usable_quantity": round(summary["usable_quantity"], 6),
            "expired_quantity": round(summary["expired_quantity"], 6),
            "stock_value": round(summary["stock_value"], 2),
        }
        for _, summary in sorted(summaries.items())
    ]
