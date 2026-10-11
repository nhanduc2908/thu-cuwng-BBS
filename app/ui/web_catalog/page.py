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
            "Danh mục quét từ thư mục HTML của dự án. Trang phân hệ có màn hình Python "
            "tương ứng được đánh dấu để mở nhanh; tài liệu, trang giới thiệu và demo "
            "không được xem là chức năng CRUD."
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
        self.summary.setText(
            f"{len(self.page_rows)} trang HTML · "
            f"{sum(bool(row['route']) for row in self.page_rows)} trang có lối tắt Python"
        )
