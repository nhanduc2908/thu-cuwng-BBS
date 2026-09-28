from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.animals.page import AnimalsPage
from app.ui.care.page import CarePage
from app.ui.dashboard.page import DashboardPage
from app.ui.health.page import HealthPage
from app.ui.imports.page import ImportsPage
from app.ui.store.page import StorePage
from app.ui.auth.dialogs import AuditLogDialog, ChangePasswordDialog
from app.ui.auth.manager import UserManagementDialog
from app.ui.sales.page import SalesPage
from app.ui.inventory.page import InventoryPage
from app.ui.reports.page import ReportsPage
from app.ui.notifications.page import OperationsPage
from app.modules.auth.constants import ROLE_LABELS
from app.ui.auth.access_page import AccessPage
from app.ui.customers.page import CustomersPage
from app.ui.reservations.page import ReservationsPage
from app.ui.suppliers.page import SuppliersPage
from app.ui.platform.page import PlatformPage


class MainWindow(QMainWindow):
    def __init__(
        self, database: Database, current_user: dict[str, Any] | None = None
    ) -> None:
        super().__init__()
        self.database = database
        self.current_user = current_user or {
            "id": None,
            "username": "local",
            "display_name": "Người dùng cục bộ",
            "role": "ADMIN",
        }
        if self.current_user["id"] is not None:
            self.database.set_actor(self.current_user["id"])
        self.setWindowTitle("Quản lý thú cưng")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        container = QWidget()
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(252)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 18)
        sidebar_layout.setSpacing(7)
        brand = QLabel("PET STORE")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(
            QLabel("QUẢN LÝ CỬA HÀNG · 15 PHÂN HỆ", objectName="sideCaption")
        )
        sidebar_layout.addSpacing(18)

        self.pages = QStackedWidget()
        self.platform = PlatformPage(database)
        self.access = AccessPage(
            database,
            self.current_user,
            self.current_user.get("id") is not None
            and self._has_permission("users.manage"),
            self._has_permission("audit.view"),
            self.manage_users,
            self.show_audit_log,
        )
        self.dashboard = DashboardPage(database)
        self.animals = AnimalsPage(database, self.refresh_dashboard)
        self.store = StorePage(database)
        self.suppliers = SuppliersPage(database)
        self.imports = ImportsPage(database, focused_section="imports")
        self.health = HealthPage(database)
        self.care = CarePage(database)
        self.customers = CustomersPage(database)
        self.reservations = ReservationsPage(database)
        self.sales = SalesPage(database, focused_section="sales")
        self.inventory = InventoryPage(database)
        self.reports = ReportsPage(database)
        self.operations = OperationsPage(database)
        for page in (
            self.platform,
            self.access,
            self.dashboard,
            self.animals,
            self.store,
            self.suppliers,
            self.imports,
            self.health,
            self.care,
            self.customers,
            self.reservations,
            self.sales,
            self.inventory,
            self.reports,
            self.operations,
        ):
            self.pages.addWidget(page)

        navigation = (
            ("HỆ THỐNG", "platform", "Nền tảng & dữ liệu", 0, "dashboard.view"),
            ("HỆ THỐNG", "access", "Tài khoản & nhật ký", 1, "access.view"),
            ("TỔNG QUAN", "dashboard", "Tổng quan", 2, "dashboard.view"),
            ("HỒ SƠ & CHĂM SÓC", "animals", "Động vật", 3, "animals.view"),
            ("HỒ SƠ & CHĂM SÓC", "health", "Sức khỏe", 7, "health.view"),
            ("HỒ SƠ & CHĂM SÓC", "care", "Chăm sóc", 8, "care.view"),
            ("HỒ SƠ & CHĂM SÓC", "store", "Chuồng trại", 4, "store.view"),
            ("NHẬP HÀNG", "suppliers", "Nhà cung cấp", 5, "imports.view"),
            ("NHẬP HÀNG", "imports", "Nhập & kiểm tra", 6, "imports.view"),
            ("KHÁCH HÀNG & BÁN HÀNG", "customers", "Khách hàng", 9, "sales.view"),
            ("KHÁCH HÀNG & BÁN HÀNG", "reservations", "Đặt trước & giữ chỗ", 10, "sales.view"),
            ("KHÁCH HÀNG & BÁN HÀNG", "sales", "Đơn hàng & thanh toán", 11, "sales.view"),
            ("VẬT TƯ & PHÂN TÍCH", "inventory", "Thức ăn & thuốc", 12, "inventory.view"),
            ("VẬT TƯ & PHÂN TÍCH", "reports", "Báo cáo", 13, "reports.view"),
            ("VẬT TƯ & PHÂN TÍCH", "operations", "Cảnh báo & sao lưu", 14, "notifications.view"),
        )

        navigation_scroll = QScrollArea()
        navigation_scroll.setWidgetResizable(True)
        navigation_scroll.setFrameShape(QFrame.Shape.NoFrame)
        navigation_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        navigation_scroll.setObjectName("navigationScroll")
        navigation_content = QWidget()
        navigation_layout = QVBoxLayout(navigation_content)
        navigation_layout.setContentsMargins(0, 0, 4, 0)
        navigation_layout.setSpacing(4)
        self.navigation_buttons: dict[str, QPushButton] = {}
        last_group = ""
        for group, route, label, index, permission in navigation:
            if permission == "access.view":
                permitted = self._has_permission(
                    "users.manage"
                ) or self._has_permission("audit.view")
            else:
                permitted = self._has_permission(permission)
            if not permitted:
                continue
            if group != last_group:
                group_label = QLabel(group, objectName="navGroupLabel")
                navigation_layout.addWidget(group_label)
                last_group = group
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, route_name=route, page_index=index: self.navigate_route(
                    route_name, page_index
                )
            )
            navigation_layout.addWidget(button)
            self.navigation_buttons[route] = button
        navigation_layout.addStretch(1)
        navigation_scroll.setWidget(navigation_content)
        sidebar_layout.addWidget(navigation_scroll, 1)

        sidebar_layout.addWidget(
            QLabel(
                f"{self.current_user['display_name']}\n"
                f"{ROLE_LABELS.get(self.current_user['role'], self.current_user['role'])}",
                objectName="sideFooter",
            )
        )
        password_button = QPushButton("Đổi mật khẩu")
        password_button.setObjectName("navButton")
        password_button.clicked.connect(self.change_password)
        sidebar_layout.addWidget(password_button)
        sidebar_layout.addWidget(
            QLabel("Quản lý nội bộ\nLưu trữ SQLite", objectName="sideFooter")
        )
        root.addWidget(sidebar)
        root.addWidget(self.pages, 1)
        self.setCentralWidget(container)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #f5f7f6; color: #23332f; font-size: 14px; }
            #sidebar { background: #173d35; }
            #navigationScroll, #navigationScroll > QWidget > QWidget {
                background: transparent; border: 0;
            }
            #navGroupLabel {
                color: #87aa9c; font-size: 9px; font-weight: 700;
                letter-spacing: 1px; padding: 12px 8px 3px;
            }
            #brand { color: white; font-size: 23px; font-weight: 700; padding: 2px 4px; }
            #sideCaption { color: #a9c6bd; font-size: 10px; padding: 0 5px; }
            #sideFooter { color: #a9c6bd; padding: 8px 5px; }
            QPushButton#navButton {
                background: transparent; color: #e5efeb; text-align: left;
                border: 0; border-radius: 7px; padding: 11px 12px;
            }
            QPushButton#navButton:hover { background: #28574c; }
            QPushButton#navButton[active="true"] {
                background: #d9eee3; color: #173d35; font-weight: 700;
            }
            QLabel#pageTitle { font-size: 25px; font-weight: 700; color: #1b3f36; }
            QLabel#sectionTitle { font-size: 17px; font-weight: 600; margin-top: 16px; }
            QFrame#statCard {
                background: white; border: 1px solid #e6ece9; border-radius: 10px;
            }
            QLabel#statValue { font-size: 30px; font-weight: 700; }
            QPushButton {
                background: white; border: 1px solid #d5dfda; border-radius: 6px;
                padding: 8px 13px;
            }
            QPushButton:hover { background: #edf3f0; }
            QPushButton#primaryButton {
                background: #287b68; color: white; border: 0; font-weight: 600;
                padding: 9px 14px;
            }
            QPushButton#primaryButton:hover { background: #1c6555; }
            QPushButton#dangerButton { color: #ae3e3e; }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QTextEdit {
                background: white; border: 1px solid #d5dfda; border-radius: 5px;
                padding: 7px;
            }
            QTableWidget {
                background: white; alternate-background-color: #f7faf8;
                border: 1px solid #e1e8e4; border-radius: 7px; gridline-color: #edf1ef;
            }
            QHeaderView::section {
                background: #edf3f0; border: 0; padding: 9px; font-weight: 600;
            }
            """
        )
        self.dashboard.refresh()
        self._configure_page_permissions()
        self.navigate_route("dashboard", 2)

    def _has_permission(self, permission: str) -> bool:
        user_id = self.current_user.get("id")
        if user_id is None:
            return True
        return self.database.has_permission(user_id, permission)

    def _configure_page_permissions(self) -> None:
        self.animals.set_manage_enabled(self._has_permission("animals.manage"))
        self.health.set_manage_enabled(self._has_permission("health.manage"))
        self.care.set_manage_enabled(self._has_permission("care.manage"))
        self.store.set_manage_enabled(self._has_permission("store.manage"))
        self.imports.set_manage_enabled(self._has_permission("imports.manage"))
        self.sales.set_manage_enabled(self._has_permission("sales.manage"))
        self.inventory.set_manage_enabled(
            self._has_permission("inventory.manage")
        )
        self.operations.set_settings_enabled(self._has_permission("settings.manage"))
        self.suppliers.set_manage_enabled(self._has_permission("imports.manage"))
        self.customers.set_manage_enabled(self._has_permission("sales.manage"))
        self.reservations.set_manage_enabled(self._has_permission("sales.manage"))
        self.access.users_button.setEnabled(self._has_permission("users.manage"))
        self.access.audit_button.setEnabled(self._has_permission("audit.view"))

    def manage_users(self) -> None:
        if not self._has_permission("users.manage"):
            QMessageBox.warning(self, "Không đủ quyền", "Bạn không có quyền quản lý tài khoản.")
            return
        UserManagementDialog(
            self, self.database, int(self.current_user["id"])
        ).exec()

    def show_audit_log(self) -> None:
        if not self._has_permission("audit.view"):
            QMessageBox.warning(self, "Không đủ quyền", "Bạn không có quyền xem nhật ký.")
            return
        AuditLogDialog(self, self.database).exec()

    def change_password(self) -> None:
        user_id = self.current_user.get("id")
        if user_id is None:
            return
        dialog = ChangePasswordDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        current, new = dialog.values()
        try:
            self.database.change_password(user_id, current, new, user_id)
        except ValueError as error:
            QMessageBox.warning(self, "Không thể đổi mật khẩu", str(error))
            return
        QMessageBox.information(self, "Đã đổi mật khẩu", "Mật khẩu đã được cập nhật.")

    def navigate(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        page = self.pages.widget(index)
        refresh = getattr(page, "refresh", None)
        if refresh:
            refresh()

    def navigate_route(self, route: str, index: int) -> None:
        if route == "operations":
            self.operations.set_section("notifications")
        self.pages.setCurrentIndex(index)
        page = self.pages.widget(index)
        refresh = getattr(page, "refresh", None)
        if refresh:
            refresh()
        for name, button in self.navigation_buttons.items():
            button.setProperty("active", name == route)
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_dashboard(self) -> None:
        self.dashboard.refresh()

    def closeEvent(self, event: Any) -> None:
        self.database.close()
        event.accept()
