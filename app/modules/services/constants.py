SERVICE_CATEGORIES = frozenset(
    {
        "BATH",
        "BATH_HYGIENE",
        "GROOMING",
        "HYGIENE",
        "PET_CARE",
        "PREMIUM",
    }
)
SERVICE_CATEGORY_LABELS = {
    "BATH": "Tắm",
    "BATH_HYGIENE": "Tắm + vệ sinh",
    "GROOMING": "Grooming",
    "HYGIENE": "Vệ sinh",
    "PET_CARE": "Chăm sóc thú cưng",
    "PREMIUM": "Premium / Spa / VIP",
}
MEMBERSHIP_MODES = frozenset(
    {"PREPAID_VISITS", "MEMBER_DISCOUNT", "RECURRING"}
)
COAT_SURCHARGE_TYPES = frozenset({"LONG", "DOUBLE", "CURLY", "THICK"})
COAT_TYPE_CODES = {
    "DÀI": "LONG",
    "HAI LỚP": "DOUBLE",
    "XOĂN": "CURLY",
    "DÀY": "THICK",
}
