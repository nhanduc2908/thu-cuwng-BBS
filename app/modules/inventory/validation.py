from datetime import date
import math
from typing import Any


def validate_day_count(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} không hợp lệ.")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{label} không hợp lệ.") from error
    if not math.isfinite(numeric_value) or not numeric_value.is_integer():
        raise ValueError(f"{label} không hợp lệ.")
    days = int(numeric_value)
    if days < (0 if allow_zero else 1):
        raise ValueError(f"{label} không hợp lệ.")
    return days


def validate_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except (TypeError, ValueError) as error:
        raise ValueError("Khoảng thời gian không hợp lệ.") from error
    if start > end:
        raise ValueError("Khoảng thời gian không hợp lệ.")
    return start, end


def finite_nonnegative(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{label} không hợp lệ.") from error
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{label} không hợp lệ.")
    return number
