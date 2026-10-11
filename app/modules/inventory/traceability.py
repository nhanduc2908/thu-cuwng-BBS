from collections.abc import Iterable, Mapping
from typing import Any


def build_batch_timeline(
    movements: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    balance = 0.0
    for movement in movements:
        quantity = float(movement["quantity"])
        movement_type = str(movement["movement_type"])
        if quantity <= 0 or movement_type not in {"IN", "OUT"}:
            raise ValueError("Giao dịch tồn kho không hợp lệ.")
        balance += quantity if movement_type == "IN" else -quantity
        timeline.append(
            {
                "movement_id": int(movement["id"]),
                "occurred_on": str(movement["occurred_on"]),
                "movement_type": movement_type,
                "quantity": quantity,
                "balance_after": round(balance, 6),
                "animal_id": movement["animal_id"],
                "reference": str(movement["reference"] or ""),
                "note": str(movement["note"] or ""),
            }
        )
    return timeline
