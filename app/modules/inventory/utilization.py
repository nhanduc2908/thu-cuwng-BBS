from collections.abc import Iterable, Mapping
from typing import Any


def summarize_animal_consumption(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        key = (int(row["animal_id"]), int(row["item_id"]))
        summary = grouped.setdefault(
            key,
            {
                "animal_id": key[0],
                "animal_code": str(row["animal_code"]),
                "animal_name": str(row["animal_name"]),
                "item_id": key[1],
                "item_code": str(row["item_code"]),
                "item_name": str(row["item_name"]),
                "unit": str(row["unit"]),
                "quantity": 0.0,
                "cost": 0.0,
            },
        )
        quantity = float(row["quantity"] or 0)
        summary["quantity"] += quantity
        summary["cost"] += quantity * float(row["unit_cost"] or 0)
    return [
        {
            **summary,
            "quantity": round(summary["quantity"], 6),
            "cost": round(summary["cost"], 2),
        }
        for _, summary in sorted(grouped.items())
    ]
