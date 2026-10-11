from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DemandForecast:
    item_id: int
    window_days: int
    horizon_days: int
    consumed_quantity: float
    average_daily_quantity: float
    projected_quantity: float
    usable_quantity: float
    days_of_stock: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplenishmentRecommendation:
    item_id: int
    item_code: str
    name: str
    average_daily_quantity: float
    usable_quantity: float
    target_quantity: float
    suggested_quantity: float
    days_of_stock: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StockValuation:
    item_id: int
    item_code: str
    name: str
    stock_quantity: float
    usable_quantity: float
    expired_quantity: float
    stock_value: float
    expired_value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LedgerDiscrepancy:
    batch_id: int
    item_id: int
    batch_code: str
    recorded_quantity: float
    ledger_quantity: float
    difference: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
