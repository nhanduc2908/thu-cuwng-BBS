from __future__ import annotations

from typing import Any


FIELD_SETS: dict[str, list[dict[str, Any]]] = {
    "customer": [
        {"name": "reference", "label": "Mã đơn / hồ sơ liên quan", "type": "text", "required": True},
        {"name": "party", "label": "Khách hàng / người nhận", "type": "text", "required": True},
        {"name": "item_code", "label": "Mã hàng / thú cưng", "type": "text"},
        {"name": "item_name", "label": "Tên hàng / thú cưng", "type": "text", "required": True},
        {"name": "quantity", "label": "Số lượng", "type": "number", "required": True},
        {"name": "unit", "label": "Đơn vị tính", "type": "text"},
        {"name": "reason", "label": "Điều kiện / lý do xuất", "type": "textarea", "required": True},
        {"name": "destination", "label": "Địa chỉ / nơi giao", "type": "text"},
        {"name": "receiver", "label": "Người nhận / người giao", "type": "text", "required": True},
        {"name": "notes", "label": "Ghi chú", "type": "textarea"},
    ],
    "inventory": [
        {"name": "reference", "label": "Mã đề nghị / hồ sơ liên quan", "type": "text", "required": True},
        {"name": "item_code", "label": "Mã hàng / mã lô", "type": "text", "required": True},
        {"name": "item_name", "label": "Tên hàng hóa", "type": "text", "required": True},
        {"name": "quantity", "label": "Số lượng xuất", "type": "number", "required": True},
        {"name": "unit", "label": "Đơn vị tính", "type": "text", "required": True},
        {"name": "lot", "label": "Lô / hạn dùng (nếu có)", "type": "text"},
        {"name": "destination", "label": "Nơi nhận / điểm đến", "type": "text", "required": True},
        {"name": "reason", "label": "Lý do và tình trạng hàng", "type": "textarea", "required": True},
        {"name": "approved_by", "label": "Người phê duyệt", "type": "text"},
        {"name": "receiver", "label": "Người nhận", "type": "text", "required": True},
        {"name": "notes", "label": "Ghi chú", "type": "textarea"},
    ],
    "animal": [
        {"name": "reference", "label": "Mã hồ sơ / lịch hẹn", "type": "text", "required": True},
        {"name": "animal_code", "label": "Mã thú cưng / microchip", "type": "text", "required": True},
        {"name": "animal_name", "label": "Tên thú cưng", "type": "text", "required": True},
        {"name": "species", "label": "Loài / giống", "type": "text", "required": True},
        {"name": "quantity", "label": "Số lượng thú cưng", "type": "number", "required": True},
        {"name": "destination", "label": "Nơi đến / đơn vị tiếp nhận", "type": "text", "required": True},
        {"name": "health_status", "label": "Tình trạng sức khỏe khi bàn giao", "type": "textarea", "required": True},
        {"name": "transport", "label": "Phương tiện / điều kiện vận chuyển", "type": "textarea"},
        {"name": "receiver", "label": "Người tiếp nhận", "type": "text", "required": True},
        {"name": "notes", "label": "Ghi chú", "type": "textarea"},
    ],
    "care": [
        {"name": "reference", "label": "Mã hồ sơ / lịch chăm sóc", "type": "text", "required": True},
        {"name": "animal_code", "label": "Mã thú cưng / microchip", "type": "text", "required": True},
        {"name": "animal_name", "label": "Tên thú cưng", "type": "text", "required": True},
        {"name": "item_name", "label": "Vật tư / dụng cụ / thuốc theo chỉ định", "type": "text", "required": True},
        {"name": "quantity", "label": "Số lượng", "type": "number", "required": True},
        {"name": "unit", "label": "Đơn vị tính", "type": "text", "required": True},
        {"name": "purpose", "label": "Mục đích / chỉ định", "type": "textarea", "required": True},
        {"name": "caregiver", "label": "Nhân viên phụ trách", "type": "text", "required": True},
        {"name": "receiver", "label": "Người nhận vật tư", "type": "text", "required": True},
        {"name": "notes", "label": "Lưu ý an toàn / dị ứng", "type": "textarea"},
    ],
    "risk": [
        {"name": "reference", "label": "Mã sự cố / báo cáo", "type": "text", "required": True},
        {"name": "item_code", "label": "Mã hàng / mã lô", "type": "text", "required": True},
        {"name": "item_name", "label": "Tên hàng / đối tượng", "type": "text", "required": True},
        {"name": "quantity", "label": "Số lượng / số cá thể", "type": "number", "required": True},
        {"name": "unit", "label": "Đơn vị tính", "type": "text"},
        {"name": "risk", "label": "Mối nguy / tình trạng phát hiện", "type": "textarea", "required": True},
        {"name": "destination", "label": "Khu vực cách ly / nơi xử lý", "type": "text", "required": True},
        {"name": "reason", "label": "Biện pháp kiểm soát", "type": "textarea", "required": True},
        {"name": "approved_by", "label": "Người phụ trách / phê duyệt", "type": "text", "required": True},
        {"name": "receiver", "label": "Người bàn giao / tiếp nhận", "type": "text", "required": True},
        {"name": "notes", "label": "Ghi chú / chứng cứ kèm theo", "type": "textarea"},
    ],
}

GROUP_LABELS = {
    "customer": "Bán hàng & bàn giao khách",
    "inventory": "Kho & vận hành cửa hàng",
    "animal": "Bàn giao thú cưng",
    "care": "Chăm sóc & thú y",
    "risk": "Chất lượng & kiểm soát rủi ro",
}


_DEFINITIONS = [
    ("ban-giao-don-da-thanh-toan", "Bàn giao đơn khách đã thanh toán", "Ngăn giao nhầm hoặc giao hàng khi đơn chưa trả đủ.", "customer", "sales.manage"),
    ("giao-hang-con-thieu", "Giao một phần đơn hàng", "Ghi nhận phần hàng giao trước và phần còn thiếu để tránh thất lạc công nợ hàng.", "customer", "sales.manage"),
    ("doi-hang-loi-cho-khach", "Đổi hàng lỗi cho khách", "Kiểm soát hàng thay thế sau khi xác minh lỗi sản phẩm.", "customer", "sales.manage"),
    ("cap-hang-bao-hanh", "Cấp hàng bảo hành", "Theo dõi vật tư hoặc sản phẩm xuất phục vụ bảo hành.", "customer", "sales.manage"),
    ("gui-mau-thu-san-pham", "Gửi mẫu thử sản phẩm", "Quản lý mẫu trải nghiệm gửi khách và tránh thất thoát hàng mẫu.", "customer", "sales.manage"),
    ("tang-qua-khuyen-mai", "Xuất quà khuyến mãi", "Theo dõi quà tặng theo chương trình và đối tượng nhận.", "customer", "sales.manage"),
    ("cho-khach-muon-hang-demo", "Cho khách mượn hàng demo", "Quản lý hàng cho mượn và thời hạn hoàn trả.", "customer", "sales.manage"),
    ("muon-hang-chup-anh", "Mượn hàng chụp ảnh nội dung", "Theo dõi sản phẩm rời kho để chụp ảnh, quay video hoặc đăng nội dung.", "inventory", "inventory.manage"),
    ("cap-hang-trung-bay", "Cấp hàng trưng bày", "Ghi nhận hàng chuyển khỏi khu lưu kho sang quầy trưng bày.", "inventory", "inventory.manage"),
    ("chuyen-hang-giua-cua-hang", "Chuyển hàng giữa cửa hàng", "Xác định điểm đi, điểm đến và người chịu trách nhiệm hàng luân chuyển.", "inventory", "inventory.manage"),
    ("chuyen-hang-ra-kho-ngoai", "Chuyển hàng sang kho ngoài", "Kiểm soát tồn đang gửi tại kho hoặc đơn vị lưu trữ bên ngoài.", "inventory", "inventory.manage"),
    ("cap-hang-gian-hang-su-kien", "Cấp hàng cho gian hàng sự kiện", "Theo dõi hàng đưa đi hội chợ, sự kiện hoặc điểm bán tạm thời.", "inventory", "inventory.manage"),
    ("lay-mau-kiem-nghiem-noi-bo", "Lấy mẫu kiểm tra chất lượng", "Lưu vết mẫu trích khỏi lô hàng để kiểm tra nội bộ.", "risk", "inventory.manage"),
    ("gui-mau-phong-thi-nghiem", "Gửi mẫu đến phòng kiểm nghiệm", "Theo dõi mẫu, đơn vị tiếp nhận và hồ sơ kiểm nghiệm.", "risk", "inventory.manage"),
    ("gui-hang-bao-hanh-nha-cung-cap", "Gửi hàng bảo hành nhà cung cấp", "Theo dõi hàng gửi nhà cung cấp sửa chữa hoặc đổi bảo hành.", "inventory", "inventory.manage"),
    ("tra-hang-thu-hoi-nha-cung-cap", "Trả lô hàng bị thu hồi", "Ghi nhận lô hàng thu hồi được xuất trả nhà cung cấp.", "risk", "inventory.manage"),
    ("tra-hang-hu-nha-cung-cap", "Trả hàng hư hỏng nhà cung cấp", "Theo dõi hàng lỗi đầu vào khi hoàn trả đối tác.", "inventory", "inventory.manage"),
    ("huy-hang-het-han", "Hủy hàng hết hạn", "Lưu chứng từ hàng quá hạn đưa khỏi khu vực kinh doanh để xử lý an toàn.", "risk", "inventory.manage"),
    ("huy-hang-vo-hong", "Hủy hàng vỡ hỏng", "Ghi nhận hàng hư hỏng không thể bán và người phê duyệt xử lý.", "risk", "inventory.manage"),
    ("cach-ly-hang-nghi-nhiem", "Cách ly hàng nghi nhiễm bẩn", "Di chuyển lô có nguy cơ nhiễm bẩn ra khỏi hàng bán thông thường.", "risk", "inventory.manage"),
    ("xuat-hang-thu-hoi-khach", "Xuất hàng phục vụ thu hồi khách", "Theo dõi hàng thay thế hoặc vật tư xử lý trong quy trình thu hồi sản phẩm.", "risk", "sales.manage"),
    ("ghi-nhan-that-thoat-ton-kho", "Ghi nhận thất thoát tồn kho", "Lập biên bản lượng hàng thiếu, nguyên nhân dự kiến và người xác nhận.", "risk", "inventory.manage"),
    ("cap-vat-tu-su-dung-noi-bo", "Cấp vật tư sử dụng nội bộ", "Theo dõi hàng tiêu hao dùng cho hoạt động cửa hàng thay vì bán.", "inventory", "inventory.manage"),
    ("cap-dung-cu-ve-sinh", "Cấp dụng cụ vệ sinh", "Kiểm soát vật tư vệ sinh và khu vực được nhận sử dụng.", "inventory", "inventory.manage"),
    ("cap-bao-bi-dong-goi", "Cấp bao bì đóng gói", "Theo dõi bao bì sử dụng cho đơn giao hàng và đóng gói tại quầy.", "inventory", "inventory.manage"),
    ("cap-vat-tu-bao-tri", "Cấp vật tư bảo trì cửa hàng", "Ghi nhận vật tư dùng sửa chữa thiết bị và cơ sở vật chất.", "inventory", "inventory.manage"),
    ("cap-phu-kien-cong-nghe", "Cấp phụ kiện công nghệ", "Bàn giao thiết bị/phụ kiện cho nhân viên kỹ thuật hoặc quầy sử dụng.", "inventory", "inventory.manage"),
    ("cap-van-phong-pham", "Cấp văn phòng phẩm", "Theo dõi vật tư hành chính xuất dùng cho từng bộ phận.", "inventory", "inventory.manage"),
    ("cap-vat-tu-cham-soc-thuong-ngay", "Cấp vật tư chăm sóc thường ngày", "Cấp định lượng vật tư tiêu hao phục vụ lịch chăm sóc thú cưng.", "care", "care.manage"),
    ("cap-vat-tu-dieu-tri-thu-y", "Cấp vật tư điều trị thú y", "Ghi nhận vật tư sử dụng theo hồ sơ và chỉ định chuyên môn.", "care", "health.manage"),
    ("cap-bo-cach-ly-thu-cung", "Cấp bộ vật tư cách ly thú cưng", "Kiểm soát vật tư phòng hộ và khu cách ly khi tiếp nhận thú nghi bệnh.", "care", "health.manage"),
    ("xuat-vat-tu-van-chuyen-khan-cap", "Xuất vật tư vận chuyển khẩn cấp", "Chuẩn bị vật tư và điều kiện vận chuyển thú cưng an toàn khi có sự cố.", "animal", "care.manage"),
    ("xuat-hang-quyen-gop-cuu-ho", "Xuất hàng quyên góp cứu hộ", "Lưu danh mục và đơn vị nhận vật tư cứu hộ động vật.", "inventory", "inventory.manage"),
    ("xuat-hang-ho-tro-nha-nuoi-tam", "Xuất hàng hỗ trợ nhà nuôi tạm", "Theo dõi vật tư hỗ trợ chăm sóc thú cưng trong thời gian lưu tạm.", "care", "care.manage"),
    ("ban-giao-thuoc-theo-chi-dinh", "Bàn giao thuốc theo chỉ định", "Ghi nhận vật tư/thuốc bàn giao cùng hướng dẫn của nhân sự thú y.", "care", "health.manage"),
    ("ban-giao-bo-nhan-nuoi", "Bàn giao bộ nhận nuôi thú cưng", "Ghi nhận thú cưng và bộ vật dụng bàn giao khi hoàn tất nhận nuôi.", "animal", "sales.manage"),
    ("cap-vat-tu-dich-vu-lam-dep", "Cấp vật tư dịch vụ làm đẹp", "Theo dõi vật tư tiêu hao sử dụng cho lịch tắm, cắt tỉa hoặc chăm sóc.", "care", "care.manage"),
    ("tra-do-ca-nhan-thu-cung-luu-tru", "Trả đồ cá nhân thú cưng lưu trú", "Đối chiếu và bàn giao lại đồ gửi kèm khi kết thúc lưu trú.", "customer", "services.manage"),
    ("chuyen-thu-cung-den-co-so-tiep-nhan", "Chuyển thú cưng đến cơ sở tiếp nhận", "Lưu tình trạng và người nhận khi chuyển thú cưng sang phòng khám/cơ sở khác.", "animal", "health.manage"),
    ("xuat-vat-tu-ung-pho-thien-tai", "Xuất vật tư ứng phó thiên tai", "Theo dõi vật tư ưu tiên cho kế hoạch sơ tán và bảo vệ thú cưng.", "risk", "inventory.manage"),
]


SLIP_TYPES: dict[str, dict[str, Any]] = {
    slug: {
        "id": slug,
        "number": index,
        "title": title,
        "problem": problem,
        "category": GROUP_LABELS[group],
        "permission": permission,
        "fields": [
            {
                "name": "issue_date",
                "label": "Ngày lập phiếu",
                "type": "date",
                "required": True,
            },
            *FIELD_SETS[group],
        ],
    }
    for index, (slug, title, problem, group, permission) in enumerate(_DEFINITIONS, 1)
}
