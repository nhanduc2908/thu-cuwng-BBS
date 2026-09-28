IMPORT_BATCH_STATUSES = ("OPEN", "COMPLETED", "CANCELLED")
INSPECTION_RESULTS = ("PASSED", "QUARANTINE", "NEEDS_TREATMENT")

IMPORT_BATCH_STATUS_LABELS = {
    "OPEN": "Đang tiếp nhận",
    "COMPLETED": "Đã kiểm tra xong",
    "CANCELLED": "Đã hủy",
}

INSPECTION_RESULT_LABELS = {
    "PASSED": "Đạt — có thể kinh doanh",
    "QUARANTINE": "Cách ly",
    "NEEDS_TREATMENT": "Cần điều trị",
}
