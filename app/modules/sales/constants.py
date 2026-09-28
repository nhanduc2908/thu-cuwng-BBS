RESERVATION_STATUSES = ("ACTIVE", "CONVERTED", "RELEASED", "EXPIRED")
ORDER_STATUSES = ("OPEN", "PARTIALLY_PAID", "PAID", "CANCELLED")
PAYMENT_METHODS = ("CASH", "BANK_TRANSFER", "CARD", "OTHER")

RESERVATION_STATUS_LABELS = {
    "ACTIVE": "Đang giữ chỗ",
    "CONVERTED": "Đã tạo đơn",
    "RELEASED": "Đã giải phóng",
    "EXPIRED": "Hết hạn",
}
ORDER_STATUS_LABELS = {
    "OPEN": "Chưa thanh toán",
    "PARTIALLY_PAID": "Thanh toán một phần",
    "PAID": "Đã thanh toán",
    "CANCELLED": "Đã hủy",
}
PAYMENT_METHOD_LABELS = {
    "CASH": "Tiền mặt",
    "BANK_TRANSFER": "Chuyển khoản",
    "CARD": "Thẻ",
    "OTHER": "Khác",
}
