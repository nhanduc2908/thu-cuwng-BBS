from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


HOME_ROUTE = ("home", "Trung tâm chức năng", 22, "dashboard.view")

ADMIN_FUNCTION_GROUPS = (
    (
        "TỔNG QUAN",
        "Theo dõi nhanh hoạt động và tình trạng cửa hàng.",
        (
            ("dashboard", "Tổng quan cửa hàng", 2, "dashboard.view",
             "Chỉ số vận hành, thú cưng và các việc cần theo dõi."),
        ),
    ),
    (
        "THÚ CƯNG & CHĂM SÓC",
        "Quản lý hồ sơ, sức khỏe, chuồng trại và công việc chăm sóc.",
        (
            ("animals", "Hồ sơ thú cưng", 3, "animals.view",
             "Danh sách và thông tin hồ sơ thú cưng."),
            ("pet_detail", "Chi tiết thú cưng", 4, "animals.view",
             "Theo dõi thông tin chi tiết của từng thú cưng."),
            ("store", "Chuồng trại", 5, "store.view",
             "Khu vực nuôi, sức chứa và bố trí."),
            ("health", "Sức khỏe", 8, "health.view",
             "Ghi nhận và tra cứu hồ sơ sức khỏe."),
            ("care", "Chăm sóc", 9, "care.view",
             "Checklist và lịch sử công việc chăm sóc."),
        ),
    ),
    (
        "NHẬP HÀNG & KHO",
        "Theo dõi nhà cung cấp, tiếp nhận hàng và tồn kho.",
        (
            ("suppliers", "Nhà cung cấp", 6, "imports.view",
             "Thông tin đối tác và nhà cung cấp."),
            ("imports", "Nhập & kiểm tra", 7, "imports.view",
             "Phiếu nhập, tiếp nhận và kiểm tra hàng."),
            ("inventory", "Kho thức ăn & thuốc", 14, "inventory.view",
             "Danh mục, số lượng và biến động tồn kho."),
        ),
    ),
    (
        "BÁN HÀNG & DỊCH VỤ",
        "Xử lý khách hàng, đơn hàng, hội viên và lịch dịch vụ nội bộ.",
        (
            ("customers", "Hồ sơ khách hàng", 10, "sales.view",
             "Hồ sơ khách hàng lưu trong hệ thống."),
            ("customer_insights", "Khách hàng & dịch vụ", 11, "sales.view",
             "Phân tích hoạt động khách hàng và dịch vụ."),
            ("reservations", "Đặt trước & giữ chỗ", 12, "sales.view",
             "Theo dõi yêu cầu đặt trước và giữ chỗ."),
            ("sales", "Đơn hàng & thanh toán", 13, "sales.view",
             "Đơn bán, thanh toán và yêu cầu storefront."),
            ("memberships", "Hội viên & hóa đơn", 17, "membership.view",
             "Gói hội viên, thẻ và hóa đơn."),
            ("services", "Dịch vụ & lịch hẹn", 18, "services.view",
             "Danh mục dịch vụ và lịch hẹn."),
            ("customer_portal", "Tài khoản cổng khách hàng", 21, "sales.manage",
             "Duyệt tài khoản và cấp mã mời từ phía nhân viên."),
        ),
    ),
    (
        "BÁO CÁO & QUẢN TRỊ",
        "Tra cứu kết quả, cảnh báo và công cụ quản trị hệ thống.",
        (
            ("reports", "Báo cáo", 15, "reports.view",
             "Báo cáo hoạt động và dữ liệu cửa hàng."),
            ("operations", "Cảnh báo & sao lưu", 16, "notifications.view",
             "Cảnh báo vận hành và công cụ dữ liệu."),
            ("platform", "Nền tảng & dữ liệu", 0, "dashboard.view",
             "Thông tin cấu hình và trạng thái hệ thống."),
            ("access", "Tài khoản & nhật ký", 1, "access.view",
             "Tài khoản nhân viên và nhật ký kiểm toán."),
            ("data_catalog", "Danh mục JSON & SQLite", 19, "reports.view",
             "Kiểm tra dữ liệu catalog và luồng nhập."),
            ("web_catalog", "Bản đồ trang HTML & Python", 20, "dashboard.view",
             "Đối chiếu các giao diện web và desktop."),
        ),
    ),
)


def routes_for_permissions(permissions: Iterable[str]) -> set[str]:
    granted = set(permissions)
    routes = {
        route
        for _group, _description, items in ADMIN_FUNCTION_GROUPS
        for route, _label, _index, permission, _hint in items
        if permission in granted
    }
    if "dashboard.view" in granted:
        routes.add(HOME_ROUTE[0])
    return routes


class AdminHomePage(QWidget):
    def __init__(
        self,
        role_label: str,
        available_routes: Iterable[str],
        navigate: Callable[[str, int], None],
    ) -> None:
        super().__init__()
        allowed = set(available_routes)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)

        heading = QLabel("Trung tâm chức năng", objectName="pageTitle")
        layout.addWidget(heading)
        description = QLabel(
            f"Không gian làm việc nội bộ · {role_label}. "
            "Các mục hiển thị theo quyền được cấp cho tài khoản."
        )
        description.setObjectName("pageSubtitle")
        description.setWordWrap(True)
        layout.addWidget(description)
        self.section_cards: dict[str, QFrame] = {}
        self.route_buttons: dict[str, QPushButton] = {}

        for title, section_description, routes in ADMIN_FUNCTION_GROUPS:
            visible_routes = [route for route in routes if route[0] in allowed]
            if not visible_routes:
                continue
            card = QFrame(objectName="adminFunctionCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 18)
            card_layout.setSpacing(10)
            card_heading = QLabel(title, objectName="sectionTitle")
            card_layout.addWidget(card_heading)
            card_summary = QLabel(section_description)
            card_summary.setObjectName("pageSubtitle")
            card_summary.setWordWrap(True)
            card_layout.addWidget(card_summary)

            actions = QGridLayout()
            actions.setHorizontalSpacing(10)
            actions.setVerticalSpacing(8)
            for index, (route, label, page_index, _permission, hint) in enumerate(
                visible_routes
            ):
                button = QPushButton(f"{label}\n{hint}")
                button.setObjectName("adminFunctionAction")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setMinimumHeight(62)
                button.setToolTip(hint)
                button.setAccessibleName(label)
                button.clicked.connect(
                    lambda _checked=False, route_name=route, target=page_index:
                    navigate(route_name, target)
                )
                actions.addWidget(button, index // 2, index % 2)
                self.route_buttons[route] = button
            card_layout.addLayout(actions)
            layout.addWidget(card)
            self.section_cards[title] = card

        layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll)
