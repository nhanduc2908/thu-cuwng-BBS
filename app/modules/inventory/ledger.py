from collections.abc import Iterable, Mapping

from app.modules.inventory.models import LedgerDiscrepancy


def find_ledger_discrepancies(
    rows: Iterable[Mapping[str, object]], tolerance: float = 0.000001
) -> list[LedgerDiscrepancy]:
    discrepancies: list[LedgerDiscrepancy] = []
    for row in rows:
        recorded = float(row["recorded_quantity"] or 0)
        ledger = float(row["ledger_quantity"] or 0)
        difference = round(recorded - ledger, 6)
        if abs(difference) > tolerance:
            discrepancies.append(
                LedgerDiscrepancy(
                    batch_id=int(row["batch_id"]),
                    item_id=int(row["item_id"]),
                    batch_code=str(row["batch_code"]),
                    recorded_quantity=round(recorded, 6),
                    ledger_quantity=round(ledger, 6),
                    difference=difference,
                )
            )
    return discrepancies
