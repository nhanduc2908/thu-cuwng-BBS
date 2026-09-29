RECOMMENDATION_CATEGORIES = (
    "FOOD",
    "HYGIENE",
    "ACCESSORY",
    "SUPPLEMENT",
    "TRAINING",
    "OTHER",
    "VETERINARY",
)

RECOMMENDATION_CATEGORY_LABELS = {
    "FOOD": "Thức ăn",
    "HYGIENE": "Vệ sinh",
    "ACCESSORY": "Phụ kiện",
    "SUPPLEMENT": "Thực phẩm bổ sung",
    "TRAINING": "Huấn luyện",
    "OTHER": "Khác",
    "VETERINARY": "Thuốc / thú y",
}

RECOMMENDATION_AGE_GROUPS = (
    "BABY",
    "YOUNG",
    "ADULT",
    "SENIOR",
)

RECOMMENDATION_AGE_LABELS = {
    "BABY": "Sơ sinh (0-3 tháng)",
    "YOUNG": "Thú non (3-12 tháng)",
    "ADULT": "Trưởng thành (1-7 tuổi)",
    "SENIOR": "Cao tuổi (từ 8 tuổi)",
}

RECOMMENDATION_EVENTS = (
    "VIEW",
    "CLICK",
    "SEARCH",
    "LIKE",
    "ADD_TO_CART",
    "PURCHASE",
    "REVIEW",
    "REMOVE_CART",
)

RECOMMENDATION_EVENT_LABELS = {
    "VIEW": "Đã xem",
    "CLICK": "Quan tâm",
    "SEARCH": "Tìm kiếm",
    "LIKE": "Yêu thích",
    "ADD_TO_CART": "Thêm giỏ",
    "PURCHASE": "Đã mua",
    "REVIEW": "Đánh giá",
    "REMOVE_CART": "Bỏ khỏi giỏ",
}

RECOMMENDATION_PURPOSES = {
    "FOOD": "Ăn uống",
    "HYGIENE": "Vệ sinh",
    "ACCESSORY": "Đi chơi / phụ kiện",
    "SUPPLEMENT": "Bổ sung dinh dưỡng",
    "TRAINING": "Huấn luyện / vận động",
    "OTHER": "Nhu cầu khác",
}

RECOMMENDATION_NEEDS = (
    ("SHEDDING", "Rụng lông"),
    ("LONG_COAT", "Lông dài"),
    ("SENSITIVE_SKIN", "Da nhạy cảm"),
    ("LOW_ACTIVITY", "Ít vận động"),
    ("HIGH_ACTIVITY", "Hoạt động nhiều"),
    ("DIGESTION", "Tiêu hóa nhạy cảm"),
    ("WEIGHT_CONTROL", "Kiểm soát cân nặng"),
    ("DENTAL_CARE", "Chăm sóc răng"),
    ("TRAINING", "Huấn luyện"),
    ("INDOOR", "Nuôi trong nhà"),
    ("OUTDOOR", "Hay ra ngoài"),
)

RECOMMENDATION_SCORE_WEIGHTS = {
    "species": 30,
    "age": 15,
    "breed": 15,
    "needs": 15,
    "behavior": 10,
    "purchase_history": 5,
    "popularity": 5,
    "stock": 5,
}
