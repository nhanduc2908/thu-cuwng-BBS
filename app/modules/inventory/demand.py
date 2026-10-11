import math

from app.modules.inventory.models import DemandForecast
from app.modules.inventory.validation import validate_day_count


def forecast_demand(
    item_id: int,
    consumed_quantity: float,
    usable_quantity: float,
    window_days: int,
    horizon_days: int,
) -> DemandForecast:
    window = validate_day_count(window_days, "Số ngày lịch sử")
    horizon = validate_day_count(horizon_days, "Số ngày dự báo")
    consumed = float(consumed_quantity)
    usable = float(usable_quantity)
    if (
        not math.isfinite(consumed)
        or not math.isfinite(usable)
        or consumed < 0
        or usable < 0
    ):
        raise ValueError("Số liệu tồn kho và tiêu thụ không hợp lệ.")
    daily = consumed / window
    days_of_stock = usable / daily if daily > 0 else None
    return DemandForecast(
        item_id=item_id,
        window_days=window,
        horizon_days=horizon,
        consumed_quantity=consumed,
        average_daily_quantity=round(daily, 6),
        projected_quantity=round(daily * horizon, 6),
        usable_quantity=usable,
        days_of_stock=round(days_of_stock, 2) if days_of_stock is not None else None,
    )
