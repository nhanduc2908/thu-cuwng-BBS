from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.common import make_table


HTML_ROOT = Path(__file__).resolve().parents[3] / "HTML"

PYTHON_TARGETS = {
    "module_01_platform.html": ("Nền tảng & dữ liệu", "platform", 0),
    "module_02_accounts.html": ("Tài khoản & nhật ký", "access", 1),
    "module_03_dashboard.html": ("Tổng quan", "dashboard", 2),
    "module_04_pets.html": ("Quản lý thú cưng", "animals", 3),
    "module_05_housing.html": ("Chuồng trại", "store", 5),
    "module_06_suppliers.html": ("Nhà cung cấp", "suppliers", 6),
    "module_07_imports.html": ("Nhập & kiểm tra", "imports", 7),
    "module_08_health.html": ("Sức khỏe", "health", 8),
    "module_09_care.html": ("Chăm sóc", "care", 9),
    "module_10_customers.html": ("Khách hàng", "customers", 10),
    "module_11_reservations.html": ("Đặt trước & giữ chỗ", "reservations", 12),
    "module_12_orders.html": ("Đơn hàng & thanh toán", "sales", 13),
    "module_13_memberships.html": ("Hội viên & bill", "memberships", 17),
    "module_14_services.html": ("Dịch vụ & lịch hẹn", "services", 18),
    "module_15_inventory.html": ("Thức ăn & thuốc", "inventory", 14),
    "module_16_reports.html": ("Báo cáo", "reports", 15),
    "module_17_alerts.html": ("Cảnh báo & sao lưu", "operations", 16),
}

PYTHON_PAGE_TARGETS = {
    "Trang hỗ trợ/data_explorer.html": ("Danh mục JSON & SQLite", "data_catalog", 19),
    "user_portal.html": (
        "Quản lý tài khoản portal",
        "customer_portal",
        21,
    ),
}

PYTHON_ROUTE_INDEX = {
    "platform": 0,
    "access": 1,
    "dashboard": 2,
    "animals": 3,
    "pet_detail": 4,
    "store": 5,
    "suppliers": 6,
    "imports": 7,
    "health": 8,
    "care": 9,
    "customers": 10,
    "customer_insights": 11,
    "reservations": 12,
    "sales": 13,
    "inventory": 14,
    "reports": 15,
    "operations": 16,
    "memberships": 17,
    "services": 18,
    "data_catalog": 19,
    "web_catalog": 20,
    "customer_portal": 21,
}

PYTHON_ROUTE_COVERAGE = (
    (
        "platform", "Nền tảng & dữ liệu",
        "Trang hỗ trợ/admin_store_management.html", "Một phần",
        "Quản trị kết nối SQLite; các thẻ tổng quan vẫn là nội dung tham khảo.",
    ),
    (
        "access", "Tài khoản & nhật ký",
        "Trang hỗ trợ/admin_store_management.html", "Một phần",
        "Có đăng nhập và xem dữ liệu theo quyền; quản lý tài khoản/audit chưa tương đương đầy đủ.",
    ),
    (
        "dashboard", "Tổng quan",
        "Trang hỗ trợ/admin_store_management.html", "Một phần",
        "Bảng tổng quan HTML còn mẫu; không thay dashboard động của Python.",
    ),
    (
        "animals", "Hồ sơ thú cưng",
        "Trang hỗ trợ/Module/module_04_pets.html", "Tham khảo",
        "Trang module là tài liệu; admin HTML chỉ xem bản ghi, chưa thay CRUD hồ sơ.",
    ),
    (
        "pet_detail", "Chi tiết thú cưng",
        "Trang hỗ trợ/pet_health_report.html", "Chưa tương đương",
        "Báo cáo HTML không tải hồ sơ thú cưng đang chọn từ SQLite.",
    ),
    (
        "store", "Chuồng trại",
        "Trang hỗ trợ/Module/module_05_housing.html", "Tham khảo",
        "Tài liệu sức chứa; chưa thay thao tác quản lý chuồng trong Python.",
    ),
    (
        "suppliers", "Nhà cung cấp",
        "Trang hỗ trợ/Module/module_06_suppliers.html", "Tham khảo",
        "Tài liệu module; admin HTML chưa có CRUD nhà cung cấp.",
    ),
    (
        "imports", "Nhập & kiểm tra",
        "Trang hỗ trợ/admin_store_management.html", "Một phần",
        "HTML có luồng lưu phiếu nhập/tiếp nhận; các nghiệp vụ kiểm tra còn dùng Python.",
    ),
    (
        "health", "Sức khỏe",
        "Trang hỗ trợ/Module/module_08_health.html", "Tham khảo",
        "Tài liệu quy trình; chưa thay CRUD hồ sơ sức khỏe.",
    ),
    (
        "care", "Chăm sóc",
        "Trang hỗ trợ/Module/module_09_care.html", "Tham khảo",
        "Tài liệu checklist; chưa thay cập nhật công việc chăm sóc.",
    ),
    (
        "customers", "Khách hàng",
        "Trang hỗ trợ/Module/module_10_customers.html", "Tham khảo",
        "Tài liệu module; admin HTML chỉ đọc dữ liệu khách hàng.",
    ),
    (
        "customer_insights", "Khách hàng & dịch vụ",
        "Trang hỗ trợ/report_kpi_board.html", "Chưa tương đương",
        "Bảng KPI HTML là nội dung tham khảo, không thay phân tích SQLite.",
    ),
    (
        "reservations", "Đặt trước & giữ chỗ",
        "Trang hỗ trợ/Module/module_11_reservations.html", "Tham khảo",
        "Tài liệu quy trình; chưa thay đặt cọc, hoàn cọc và chuyển trạng thái.",
    ),
    (
        "sales", "Đơn hàng & thanh toán",
        "Trang hỗ trợ/admin_store_management.html", "Một phần",
        "Admin xem đơn và yêu cầu website; chưa thay tạo đơn, ghi thanh toán hoặc xử lý tồn.",
    ),
    (
        "inventory", "Kho thức ăn & thuốc",
        "Web bán hàng/san-pham.html", "Một phần",
        "Website tra cứu catalog; không thay quản lý mặt hàng, lô và biến động kho.",
    ),
    (
        "reports", "Báo cáo",
        "Trang hỗ trợ/data_explorer.html", "Một phần",
        "Tra cứu/xuất dữ liệu đã chuẩn bị; chưa thay báo cáo vận hành trực tiếp.",
    ),
    (
        "operations", "Cảnh báo & sao lưu",
        "Trang hỗ trợ/operations_snapshot.html", "Tham khảo",
        "Ảnh chụp vận hành; chưa thay cảnh báo và sao lưu thực.",
    ),
    (
        "memberships", "Hội viên & hóa đơn",
        "Trang hỗ trợ/Module/module_13_memberships.html", "Tham khảo",
        "Tài liệu module; chưa thay quản lý gói, hội viên và hóa đơn.",
    ),
    (
        "services", "Dịch vụ & lịch hẹn",
        "Trang hỗ trợ/Module/module_14_services.html", "Tham khảo",
        "Tài liệu module; chưa thay điều phối lịch hẹn.",
    ),
    (
        "data_catalog", "Danh mục JSON & nhập SQLite",
        "Trang hỗ trợ/data_explorer.html", "Một phần",
        "Xem/xuất dữ liệu; thao tác nhập SQLite vẫn cần quyền và luồng quản trị.",
    ),
    (
        "web_catalog", "Bản đồ trang HTML & Python",
        "Trang hỗ trợ/Module/index.html", "Tham khảo",
        "Thư viện tài liệu không tự đối chiếu toàn bộ route Python.",
    ),
    (
        "customer_portal", "Tài khoản portal khách hàng",
        "TRrang chính/user_portal.html", "Một phần",
        "Có portal khách hàng; quản trị tài khoản/liên kết vẫn cần màn Python.",
    ),
)

REFERENCE_PAGES = {
    "admin_store_management.html": (
        "HTML quản trị kết nối SQLite cục bộ; Python có các màn hình CRUD chuyên biệt."
    ),
    "petcare_management.html": (
        "Bảng điều khiển HTML; dùng ứng dụng Python cho nghiệp vụ CRUD đầy đủ."
    ),
    "user_portal.html": (
        "Cổng khách hàng; dùng dữ liệu tài khoản đã được liên kết, không phải trang demo."
    ),
    "index_customer.html": "Trang giới thiệu demo, không có đăng nhập hay dữ liệu khách thật.",
    "disease_support.html": "Tài liệu tham khảo; nội dung không thay thế chẩn đoán thú y.",
}


class WebCatalogPage(QWidget):
    def __init__(
        self,
        open_html: Callable[[str], None],
        open_python: Callable[[str, int], None],
        available_routes: set[str],
    ) -> None:
        super().__init__()
        self.open_html = open_html
        self.open_python = open_python
        self.available_routes = available_routes
        self.page_rows: list[dict[str, str]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Bản đồ trang HTML & Python", objectName="pageTitle"))
        description = QLabel(
            "Danh mục quét từ thư mục HTML của dự án và đối chiếu với 22 màn hình Python. "
            "Bảng độ phủ nêu trang HTML gần nhất cùng giới hạn thay thế; tài liệu, trang "
            "giới thiệu và demo không được xem là chức năng CRUD."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.summary = QLabel()
        self.summary.setObjectName("pageSubtitle")
        layout.addWidget(self.summary)
        self.table = make_table(
            ["Trang HTML", "Nhóm", "Phân loại / giới hạn", "Python tương ứng", "Mở"]
        )
        layout.addWidget(self.table, 1)
        layout.addWidget(
            QLabel("Độ phủ HTML cho các màn hình Python", objectName="pageSubtitle")
        )
        self.coverage_table = make_table(
            ["Màn hình Python", "HTML phù hợp nhất", "Mức thay thế", "Giới hạn", "Mở"]
        )
        layout.addWidget(self.coverage_table, 1)
        self.refresh()

    def refresh(self, *_: object) -> None:
        paths = sorted(
            (
                path
                for path in HTML_ROOT.rglob("*.html")
                if path.is_file()
            ),
            key=lambda path: path.relative_to(HTML_ROOT).as_posix().casefold(),
        )
        self.page_rows = []
        for path in paths:
            relative = path.relative_to(HTML_ROOT).as_posix()
            name = path.name
            target = PYTHON_TARGETS.get(name) if "/Module/" in relative else None
            target = target or PYTHON_PAGE_TARGETS.get(relative) or PYTHON_PAGE_TARGETS.get(name)
            target_label = target[0] if target else "—"
            route = target[1] if target else ""
            if target and route not in self.available_routes:
                target_label = "Không đủ quyền xem màn hình Python"
                route = ""
            if name == "user_portal.html":
                classification = "Cổng khách hàng HTML; quản lý tài khoản bằng Python"
            elif target:
                classification = "Có màn hình Python tương ứng"
            elif name in REFERENCE_PAGES:
                classification = REFERENCE_PAGES[name]
            elif relative in {"index.html", "menu.html"}:
                classification = "Trang điều hướng / danh mục"
            elif relative.startswith("Trang hỗ trợ/"):
                classification = "Tài liệu hoặc trang hỗ trợ; không thay CRUD"
            elif relative.startswith("TRrang chính/"):
                classification = "Trang giới thiệu / sản phẩm; không thay CRUD"
            else:
                classification = "Trang nội dung"

            if relative.startswith("Trang hỗ trợ/"):
                group = "Hỗ trợ"
            elif relative.startswith("TRrang chính/"):
                group = "Trang chính"
            else:
                group = "Điều hướng"

            self.page_rows.append(
                {
                    "path": relative,
                    "group": group,
                    "classification": classification,
                    "target_label": target_label,
                    "route": route,
                }
            )

        self.table.setRowCount(len(self.page_rows))
        for row_index, row in enumerate(self.page_rows):
            for column, key in enumerate(
                ("path", "group", "classification", "target_label")
            ):
                self.table.setItem(
                    row_index, column, QTableWidgetItem(row[key])
                )
            actions = QWidget()
            action_layout = QHBoxLayout(actions)
            action_layout.setContentsMargins(3, 2, 3, 2)
            html_button = QPushButton("Mở HTML")
            html_button.clicked.connect(
                lambda _checked=False, page_path=row["path"]: self.open_html(
                    "/" + page_path
                )
            )
            action_layout.addWidget(html_button)
            if row["route"]:
                python_button = QPushButton("Mở Python")
                route_target = next(
                    target
                    for target in (*PYTHON_TARGETS.values(), *PYTHON_PAGE_TARGETS.values())
                    if target[1] == row["route"]
                )
                python_button.clicked.connect(
                    lambda _checked=False, target=route_target: self.open_python(
                        target[1], target[2]
                    )
                )
                action_layout.addWidget(python_button)
            self.table.setCellWidget(row_index, 4, actions)
        self.coverage_table.setRowCount(len(PYTHON_ROUTE_COVERAGE))
        for row_index, (route, label, html_path, coverage, limitation) in enumerate(
            PYTHON_ROUTE_COVERAGE
        ):
            values = (label, html_path, coverage, limitation)
            for column, value in enumerate(values):
                self.coverage_table.setItem(
                    row_index, column, QTableWidgetItem(value)
                )
            actions = QWidget()
            action_layout = QHBoxLayout(actions)
            action_layout.setContentsMargins(3, 2, 3, 2)
            html_button = QPushButton("Mở HTML")
            html_button.setEnabled((HTML_ROOT / html_path).is_file())
            html_button.clicked.connect(
                lambda _checked=False, page_path=html_path: self.open_html(
                    "/" + page_path
                )
            )
            action_layout.addWidget(html_button)
            if route in self.available_routes:
                python_button = QPushButton("Mở Python")
                python_button.clicked.connect(
                    lambda _checked=False, route_name=route: self.open_python(
                        route_name, PYTHON_ROUTE_INDEX[route_name]
                    )
                )
                action_layout.addWidget(python_button)
            else:
                action_layout.addWidget(QLabel("Không đủ quyền"))
            self.coverage_table.setCellWidget(row_index, 4, actions)
        self.summary.setText(
            f"{len(self.page_rows)} trang HTML · "
            f"{sum(bool(row['route']) for row in self.page_rows)} trang có lối tắt Python · "
            f"{len(PYTHON_ROUTE_COVERAGE)} màn hình Python đã đối chiếu"
        )
