from datetime import date

from app.modules.inventory.validation import validate_day_count


def expiry_bucket(expiry_date: str | None, today: date | None = None) -> str:
    if not expiry_date:
        return "NO_EXPIRY"
    try:
        expiry = date.fromisoformat(expiry_date)
    except (TypeError, ValueError) as error:
        raise ValueError("Ngày hết hạn không hợp lệ.") from error
    current = today or date.today()
    days_remaining = (expiry - current).days
    if days_remaining < 0:
        return "EXPIRED"
    if days_remaining <= 7:
        return "DUE_7_DAYS"
    if days_remaining <= 30:
        return "DUE_30_DAYS"
    return "LATER"


def validate_expiry_window(days: int) -> int:
    return validate_day_count(days, "Số ngày cảnh báo", allow_zero=True)
