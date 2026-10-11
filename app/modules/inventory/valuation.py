from collections.abc import Iterable, Mapping

from app.modules.inventory.models import StockValuation


def value_stock(rows: Iterable[Mapping[str, object]]) -> list[StockValuation]:
    valuations: list[StockValuation] = []
    for row in rows:
        stock_quantity = float(row["stock_quantity"] or 0)
        usable_quantity = float(row["usable_quantity"] or 0)
        expired_quantity = float(row["expired_quantity"] or 0)
        stock_value = float(row["stock_value"] or 0)
        expired_value = float(row["expired_value"] or 0)
        valuations.append(
            StockValuation(
                item_id=int(row["item_id"]),
                item_code=str(row["item_code"]),
                name=str(row["name"]),
                stock_quantity=round(stock_quantity, 6),
                usable_quantity=round(usable_quantity, 6),
                expired_quantity=round(expired_quantity, 6),
                stock_value=round(stock_value, 2),
                expired_value=round(expired_value, 2),
            )
        )
    return valuations
