import math

from app.modules.inventory.models import ReplenishmentRecommendation
from app.modules.inventory.validation import validate_day_count


def recommend_replenishment(
    *,
    item_id: int,
    item_code: str,
    name: str,
    average_daily_quantity: float,
    usable_quantity: float,
    minimum_stock: float,
    lead_time_days: int,
    safety_days: int,
    days_of_stock: float | None,
) -> ReplenishmentRecommendation:
    lead_time = validate_day_count(lead_time_days, "Thời gian cung ứng", allow_zero=True)
    safety = validate_day_count(safety_days, "Số ngày dự phòng", allow_zero=True)
    daily = float(average_daily_quantity)
    usable = float(usable_quantity)
    minimum = float(minimum_stock)
    if any(not math.isfinite(value) or value < 0 for value in (daily, usable, minimum)):
        raise ValueError("Số liệu đặt hàng lại không hợp lệ.")
    target = daily * (lead_time + safety) + minimum
    return ReplenishmentRecommendation(
        item_id=item_id,
        item_code=item_code,
        name=name,
        average_daily_quantity=round(daily, 6),
        usable_quantity=round(usable, 6),
        target_quantity=round(target, 6),
        suggested_quantity=round(max(0.0, target - usable), 6),
        days_of_stock=days_of_stock,
    )
