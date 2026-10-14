from typing import Any
from urllib.parse import quote

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
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
from app.project_share import ProjectShareServer
from app.ui.animals.page import AnimalsPage
from app.ui.admin_home_page import (
    ADMIN_FUNCTION_GROUPS,
    HOME_ROUTE,
    AdminHomePage,
    routes_for_permissions,
)
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
from app.ui.customer_insights.page import CustomerPetServiceDashboardPage
from app.ui.pet_detail.page import PetDetailPage
from app.ui.reservations.page import ReservationsPage
from app.ui.suppliers.page import SuppliersPage
from app.ui.platform.page import PlatformPage
from app.ui.memberships.page import MembershipPage
from app.ui.services.page import ServicesPage
from app.ui.data_catalog.page import DataCatalogPage
from app.ui.web_catalog.page import WebCatalogPage
from app.ui.customer_portal.page import CustomerPortalPage
from app.ui.project_share_dialog import ProjectShareDialog


class _UnavailablePage(QWidget):
    def __init__(self, message: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch(1)

    def refresh(self, *_: object) -> None:
        return

    def set_manage_enabled(self, _enabled: bool) -> None:
        return

    def set_settings_enabled(self, _enabled: bool) -> None:
        return

    def set_import_enabled(self, _enabled: bool) -> None:
        return

    def set_access(self, *_: bool) -> None:
        return


class MainWindow(QMainWindow):
    def __init__(
        self,
        database: Database,
        current_user: dict[str, Any] | None = None,
        web_base_url: str | None = None,
        project_share_server: ProjectShareServer | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.web_base_url = web_base_url.rstrip("/") if web_base_url else None
        self.project_share_server = project_share_server
        self.current_user = current_user or {
            "id": None,
            "username": "local",
            "display_name": "Người dùng cục bộ",
            "role": "ADMIN",
        }
        if self.current_user["id"] is not None:
            self.database.set_actor(self.current_user["id"])
        self.setWindowTitle("Bông Bông Pet Care · Quản trị cửa hàng")
        self.resize(1360, 860)
        self.setMinimumSize(980, 640)
        self.remote_mode = bool(getattr(database, "is_remote", False))

        container = QWidget()
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(264)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 22, 16, 16)
        sidebar_layout.setSpacing(6)
        brand = QLabel("🐾 BÔNG BÔNG")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(
            QLabel("PET CARE · KHU VỰC NỘI BỘ", objectName="sideCaption")
        )
        sidebar_layout.addSpacing(18)

        self.pages = QStackedWidget()
        self.platform = (
            _UnavailablePage(
                "Thông tin nền tảng và đường dẫn SQLite chỉ có trong chế độ cục bộ."
            )
            if self.remote_mode
            else PlatformPage(database)
        )
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
        self.animals = self._page(
            "animals.view", lambda: AnimalsPage(database, self.refresh_dashboard)
        )
        self.pet_detail = self._page(
            "animals.view", lambda: PetDetailPage(database)
        )
        self.store = self._page("store.view", lambda: StorePage(database))
        self.suppliers = self._page(
            "imports.view", lambda: SuppliersPage(database)
        )
        self.imports = self._page(
            "imports.view",
            lambda: ImportsPage(database, focused_section="imports"),
        )
        self.health = self._page("health.view", lambda: HealthPage(database))
        self.care = self._page("care.view", lambda: CarePage(database))
        self.customers = self._page(
            "sales.view", lambda: CustomersPage(database)
        )
        self.customer_insights = self._page(
            "sales.view", lambda: CustomerPetServiceDashboardPage(database)
        )
        self.reservations = self._page(
            "sales.view", lambda: ReservationsPage(database)
        )
        self.sales = self._page(
            "sales.view", lambda: SalesPage(database, focused_section="sales")
        )
        self.inventory = self._page(
            "inventory.view", lambda: InventoryPage(database)
        )
        self.reports = self._page(
            "reports.view", lambda: ReportsPage(database)
        )
        self.operations = self._page(
            ("notifications.view", "settings.manage"),
            lambda: OperationsPage(database),
        )
        self.memberships = self._page(
            "membership.view",
            lambda: MembershipPage(
                database, self._has_permission("membership.manage")
            ),
        )
        self.services = self._page(
            "services.view",
            lambda: ServicesPage(
                database,
                self._has_permission("services.manage"),
                self._has_permission("services.catalog.manage"),
            ),
        )
        self.data_catalog = (
            _UnavailablePage(
                "Nhập dữ liệu từ thư mục máy tính chỉ có trong chế độ cục bộ."
            )
            if self.remote_mode
            else DataCatalogPage(
                database, self._has_permission("settings.manage")
            )
        )
        self.customer_portal = CustomerPortalPage(
            database,
            self.current_user.get("id") is not None
            and self._has_permission("sales.manage"),
        )
        route_permissions = {
            permission
            for _group, _description, routes in ADMIN_FUNCTION_GROUPS
            for _route, _label, _index, permission, _hint in routes
        }
        granted_permissions = {
            permission
            for permission in route_permissions | {"users.manage", "audit.view"}
            if self._has_permission(permission)
        }
        self.available_admin_routes = routes_for_permissions(granted_permissions)
        available_python_routes = {
            route
            for route in self.available_admin_routes
            if route not in {"access", HOME_ROUTE[0]}
        }
        self.web_catalog = WebCatalogPage(
            self.open_web_page,
            self.navigate_route,
            available_python_routes,
        )
        self.admin_home = AdminHomePage(
            ROLE_LABELS.get(
                self.current_user["role"], self.current_user["role"]
            ),
            self.available_admin_routes,
            self.navigate_route,
        )
        for page in (
            self.platform,
            self.access,
            self.dashboard,
            self.animals,
            self.pet_detail,
            self.store,
            self.suppliers,
            self.imports,
            self.health,
            self.care,
            self.customers,
            self.customer_insights,
            self.reservations,
            self.sales,
            self.inventory,
            self.reports,
            self.operations,
            self.memberships,
            self.services,
            self.data_catalog,
            self.web_catalog,
            self.customer_portal,
            self.admin_home,
        ):
            self.pages.addWidget(page)

        navigation = [
            ("KHU VỰC NỘI BỘ", *HOME_ROUTE),
            *(
                (group, route, label, index, permission)
                for group, _description, routes in ADMIN_FUNCTION_GROUPS
                for route, label, index, permission, _hint in routes
            ),
        ]

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

        user_identity = QLabel(
                f"{self.current_user['display_name']}\n"
                f"{ROLE_LABELS.get(self.current_user['role'], self.current_user['role'])}",
                objectName="sideFooter",
            )
        user_identity.setWordWrap(True)
        sidebar_layout.addWidget(user_identity)
        password_button = QPushButton("Đổi mật khẩu")
        password_button.setObjectName("navButton")
        password_button.clicked.connect(self.change_password)
        sidebar_layout.addWidget(password_button)
        storage_caption = (
            "Không gian vận hành nội bộ\nDữ liệu đồng bộ qua API trung tâm"
            if self.remote_mode
            else "Không gian vận hành nội bộ\nDữ liệu lưu trong SQLite"
        )
        sidebar_layout.addWidget(QLabel(storage_caption, objectName="sideFooter"))
        root.addWidget(sidebar)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        topbar = QFrame(objectName="appTopbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(26, 12, 26, 12)
        topbar_layout.addWidget(
            QLabel("BÔNG BÔNG PET CARE  /  KHÔNG GIAN QUẢN TRỊ", objectName="topbarBrand")
        )
        topbar_layout.addStretch()
        self.website_button = QPushButton("Mở website")
        self.website_button.setObjectName("websiteButton")
        self.website_button.setToolTip("Mở trang giới thiệu và thư viện dự án HTML")
        self.website_button.setEnabled(self.web_base_url is not None)
        self.website_button.clicked.connect(
            lambda: self.open_web_page("/index.html")
        )
        topbar_layout.addWidget(self.website_button)
        self.storefront_button = QPushButton("Mở cửa hàng")
        self.storefront_button.setObjectName("storefrontButton")
        self.storefront_button.setToolTip(
            "Mở trang bán hàng dùng catalog SQLite của ứng dụng"
        )
        self.storefront_button.setEnabled(self.web_base_url is not None)
        self.storefront_button.clicked.connect(
            lambda: self.open_web_page("/Web bán hàng/index.html")
        )
        topbar_layout.addWidget(self.storefront_button)
        self.admin_web_button = QPushButton("Quản trị web")
        self.admin_web_button.setObjectName("adminWebButton")
        self.admin_web_button.setToolTip(
            "Giao diện quản trị HTML chỉ được hỗ trợ khi desktop dùng SQLite cục bộ"
            if self.remote_mode
            else "Mở giao diện quản trị HTML kết nối SQLite"
        )
        self.admin_web_button.setEnabled(
            self.web_base_url is not None and not self.remote_mode
        )
        self.admin_web_button.clicked.connect(
            lambda: self.open_web_page("/Trang hỗ trợ/admin_store_management.html")
        )
        topbar_layout.addWidget(self.admin_web_button)
        self.project_share_button = QPushButton("Chia sẻ quan sát")
        self.project_share_button.setObjectName("projectShareButton")
        self.project_share_button.setVisible(
            self.project_share_server is not None
            and self._has_permission("settings.manage")
        )
        self.project_share_button.clicked.connect(self.open_project_share)
        topbar_layout.addWidget(self.project_share_button)
        topbar_layout.addWidget(
            QLabel(
                f"Xin chào, {self.current_user['display_name']}\n"
                f"{ROLE_LABELS.get(self.current_user['role'], self.current_user['role'])}",
                objectName="topbarUser",
            )
        )
        content_layout.addWidget(topbar)
        content_layout.addWidget(self.pages, 1)
        root.addWidget(content, 1)
        self.setCentralWidget(container)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #f3f7f3; color: #20382e; font-size: 14px; }
            #sidebar { background: #12372b; }
            #navigationScroll, #navigationScroll > QWidget > QWidget {
                background: transparent; border: 0;
            }
            #navGroupLabel {
                color: #9dbca9; font-size: 9px; font-weight: 800;
                letter-spacing: 1px; padding: 15px 9px 4px;
            }
            #brand { color: #fff; font-size: 20px; font-weight: 850; padding: 2px 4px; letter-spacing: 1px; }
            #sideCaption { color: #c2d7cb; font-size: 9px; font-weight: 700; padding: 0 5px; letter-spacing: .7px; }
            #sideFooter { color: #d0e1d6; padding: 10px 8px; border-top: 1px solid #315343; }
            #appTopbar { background: #fff; border-bottom: 1px solid #dfe8e1; }
            #topbarBrand { color: #527261; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
            #topbarUser {
                color: #20382e; font-family: "Segoe UI"; font-size: 12px;
                font-weight: 600;
            }
            QPushButton#navButton {
                background: transparent; color: #e4eee7; text-align: left;
                border: 0; border-radius: 8px; padding: 10px 12px;
            }
            QPushButton#navButton:hover { background: #214936; color: #fff; }
            QPushButton#navButton[active="true"] {
                background: #dcefe1; color: #12372b; font-weight: 800;
            }
            QLabel#pageTitle { font-size: 26px; font-weight: 800; color: #173d2c; }
            QLabel#pageSubtitle { font-size: 15px; font-weight: 800; color: #24563d; }
            QLabel#sectionTitle { font-size: 17px; font-weight: 750; margin-top: 14px; color: #24563d; }
            QFrame#adminFunctionCard {
                background: #fff; border: 1px solid #dfe9e1; border-radius: 14px;
            }
            QPushButton#adminFunctionAction {
                background: #f8fbf8; color: #20382e; text-align: left;
                border: 1px solid #dfe9e1; border-radius: 10px;
                padding: 10px 12px; font-weight: 750;
            }
            QPushButton#adminFunctionAction:hover {
                background: #edf6ef; border-color: #9fc6aa;
            }
            QFrame#statCard, QWidget#profileCard, QFrame#profileCard {
                background: #fff; border: 1px solid #dfe9e1; border-radius: 12px;
            }
            QLabel#statValue { font-size: 30px; font-weight: 700; }
            QPushButton {
                background: #fff; border: 1px solid #d9e4dc; border-radius: 8px;
                padding: 8px 13px;
            }
            QPushButton:hover { background: #edf6ef; border-color: #a9c9b2; }
            QPushButton#primaryButton {
                background: #176b4b; color: white; border: 0; font-weight: 700;
                padding: 9px 14px;
            }
            QPushButton#primaryButton:hover { background: #10553b; }
            QPushButton#dangerButton { color: #ae3e3e; }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QTextEdit {
                background: #fff; border: 1px solid #d7e2da; border-radius: 7px;
                padding: 7px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus,
            QDoubleSpinBox:focus, QTextEdit:focus {
                border: 1px solid #37835f;
            }
            QTableWidget {
                background: #fff; alternate-background-color: #f5f9f5;
                border: 1px solid #dfe8e1; border-radius: 9px; gridline-color: #edf2ee;
                selection-background-color: #dcefe1; selection-color: #173d2c;
            }
            QHeaderView::section {
                background: #edf4ee; color: #315941; border: 0; padding: 9px; font-weight: 800;
            }
            QTabBar::tab {
                background: #eaf1eb; padding: 9px 16px; margin-right: 3px;
                border-top-left-radius: 7px; border-top-right-radius: 7px;
            }
            QTabBar::tab:selected { background: #fff; color: #176b4b; font-weight: 800; }
            QCheckBox { spacing: 8px; color: #315941; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            """
        )
        self.dashboard.refresh()
        self._configure_page_permissions()
        self.navigate_route(HOME_ROUTE[0], HOME_ROUTE[2])

    def _has_permission(self, permission: str) -> bool:
        user_id = self.current_user.get("id")
        if user_id is None:
            return True
        return self.database.has_permission(user_id, permission)

    def _page(
        self,
        permissions: str | tuple[str, ...],
        create_page: Any,
    ) -> QWidget:
        if not self.remote_mode:
            return create_page()
        required = (permissions,) if isinstance(permissions, str) else permissions
        if any(self._has_permission(permission) for permission in required):
            return create_page()
        return _UnavailablePage("Bạn không có quyền truy cập chức năng này.")

    def _configure_page_permissions(self) -> None:
        self.animals.set_manage_enabled(self._has_permission("animals.manage"))
        self.health.set_manage_enabled(self._has_permission("health.manage"))
        self.care.set_manage_enabled(self._has_permission("care.manage"))
        self.store.set_manage_enabled(self._has_permission("store.manage"))
        self.imports.set_manage_enabled(self._has_permission("imports.manage"))
        sales_manage = self._has_permission("sales.manage")
        sales_request = self._has_permission("sales.request")
        sales_approve = self._has_permission("sales.approve")
        self.sales.set_access(sales_manage, sales_request, sales_approve)
        self.inventory.set_manage_enabled(
            self._has_permission("inventory.manage")
        )
        self.operations.set_settings_enabled(self._has_permission("settings.manage"))
        self.memberships.set_manage_enabled(
            self._has_permission("membership.manage")
        )
        self.suppliers.set_manage_enabled(self._has_permission("imports.manage"))
        self.customers.set_access(sales_manage, sales_request, sales_approve)
        self.reservations.set_access(sales_manage, sales_request, sales_approve)
        self.data_catalog.set_import_enabled(self._has_permission("settings.manage"))
        self.customer_portal.set_manage_enabled(
            self.current_user.get("id") is not None
            and self._has_permission("sales.manage")
        )
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

    def open_web_page(self, path: str) -> None:
        if self.web_base_url is None:
            QMessageBox.warning(
                self,
                "Website chưa sẵn sàng",
                "Không thể mở website vì cầu nối web cục bộ chưa được khởi động.",
            )
            return
        encoded_path = quote(path, safe="/")
        if not QDesktopServices.openUrl(QUrl(f"{self.web_base_url}{encoded_path}")):
            QMessageBox.warning(
                self,
                "Không thể mở website",
                "Không tìm thấy trình duyệt mặc định để mở trang PetCare.",
            )

    def open_project_share(self) -> None:
        if not self._has_permission("settings.manage"):
            QMessageBox.warning(
                self, "Không đủ quyền", "Bạn không có quyền quản lý chia sẻ dự án."
            )
            return
        if self.project_share_server is None:
            QMessageBox.warning(
                self, "Chia sẻ chưa sẵn sàng", "Máy chủ chia sẻ chưa được khởi tạo."
            )
            return
        ProjectShareDialog(
            self, self.project_share_server, self.manage_users
        ).exec()

    def closeEvent(self, event: Any) -> None:
        if self.project_share_server is not None:
            self.project_share_server.stop()
        self.database.close()
        event.accept()
