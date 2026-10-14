import sqlite3
import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.sales.constants import (
    ORDER_STATUS_LABELS,
    PAYMENT_METHOD_LABELS,
    RESERVATION_STATUS_LABELS,
)
from app.ui.common import make_table, set_cell
from app.ui.sales.dialogs import (
    CustomerDialog,
    PaymentDialog,
    ProductSalesOrderDialog,
    RefundDepositDialog,
    ReservationDialog,
    SalesOrderDialog,
)


class SalesPage(QWidget):
    def __init__(
        self, database: Database, focused_section: str | None = None
    ) -> None:
        super().__init__()
        self.database = database
        self.manage_enabled = True
        self.request_enabled = True
        self.approve_enabled = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        page_titles = {
            None: "Khách hàng và bán hàng",
            "customers": "Khách hàng",
            "reservations": "Đặt trước & giữ chỗ",
            "sales": "Đơn hàng & thanh toán",
        }
        if focused_section not in page_titles:
            raise ValueError(f"Phân hệ bán hàng không hợp lệ: {focused_section}")
        layout.addWidget(QLabel(page_titles[focused_section], objectName="pageTitle"))
        self.tabs = QTabWidget()
        self.customers_tab = self._build_customers_tab()
        self.reservations_tab = self._build_reservations_tab()
        self.orders_tab = self._build_orders_tab()
        self.approvals_tab = self._build_approvals_tab()
        self.tabs.addTab(self.customers_tab, "Khách hàng")
        self.tabs.addTab(self.reservations_tab, "Đặt trước")
        self.tabs.addTab(self.orders_tab, "Đơn hàng & thanh toán")
        self.tabs.addTab(self.approvals_tab, "Duyệt bán hàng")
        if focused_section is not None:
            section_indexes = {"customers": 0, "reservations": 1, "sales": 2}
            section_index = section_indexes.get(focused_section)
            self.tabs.setCurrentIndex(section_index)
            self.tabs.tabBar().hide()
        layout.addWidget(self.tabs)
        self.refresh_customers()
        self.refresh_reservations()
        self.refresh_orders()

    def _build_customers_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        toolbar = QHBoxLayout()
        toolbar.addStretch()
        self.add_customer_button = QPushButton(
            "+ Thêm khách hàng", objectName="primaryButton"
        )
        self.add_customer_button.clicked.connect(self.add_customer)
        toolbar.addWidget(self.add_customer_button)
        layout.addLayout(toolbar)
        self.customers_table = make_table(
            ["Mã", "Khách hàng", "Điện thoại", "Email", "Đơn hàng", "Đã thanh toán"]
        )
        layout.addWidget(self.customers_table)

        detail_widget = QWidget()
        detail_layout = QHBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 12, 0, 0)

        profile_box = QWidget(objectName="profileCard")
        profile_box_layout = QVBoxLayout(profile_box)
        profile_box_layout.setContentsMargins(12, 12, 12, 12)
        self.customer_profile_title = QLabel("Hồ sơ khách hàng")
        self.customer_profile_title.setObjectName("pageSubtitle")
        profile_box_layout.addWidget(self.customer_profile_title)

        profile_grid = QGridLayout()
        profile_grid.setColumnStretch(0, 0)
        profile_grid.setColumnStretch(1, 1)
        self.customer_profile_name = QLabel("-")
        self.customer_profile_phone = QLabel("-")
        self.customer_profile_email = QLabel("-")
        self.customer_profile_address = QLabel("-")
        self.customer_profile_note = QLabel("-")

        labels = [
            ("Khách hàng", self.customer_profile_name),
            ("Điện thoại", self.customer_profile_phone),
            ("Email", self.customer_profile_email),
            ("Địa chỉ", self.customer_profile_address),
            ("Ghi chú", self.customer_profile_note),
        ]
        for index, (text, value_label) in enumerate(labels):
            title = QLabel(f"{text}:")
            title.setStyleSheet("font-weight: 600; color: #31445d;")
            profile_grid.addWidget(title, index, 0)
            profile_grid.addWidget(value_label, index, 1)
        profile_box_layout.addLayout(profile_grid)
        detail_layout.addWidget(profile_box, 2)

        pets_box = QWidget(objectName="profileCard")
        pets_layout = QVBoxLayout(pets_box)
        pets_layout.setContentsMargins(12, 12, 12, 12)
        pets_title = QLabel("Thú cưng của khách hàng")
        pets_title.setObjectName("pageSubtitle")
        pets_layout.addWidget(pets_title)
        self.customer_pets_table = make_table(
            ["Tên thú cưng", "Loài", "Giống", "Tuổi", "Cân nặng", "Trạng thái"]
        )
        pets_layout.addWidget(self.customer_pets_table)
        self.customer_pets_table.currentCellChanged.connect(
            self._selected_pet_changed
        )

        pet_detail_box = QWidget(objectName="profileCard")
        pet_detail_layout = QVBoxLayout(pet_detail_box)
        pet_detail_layout.setContentsMargins(12, 12, 12, 12)
        pet_detail_layout.addWidget(QLabel("Pet detail", objectName="pageSubtitle"))

        pet_header = QHBoxLayout()
        self.pet_avatar = QLabel("🐾")
        self.pet_avatar.setStyleSheet(
            "font-size: 30px; background: #f7f0df; border-radius: 18px; min-width: 60px; min-height: 60px; qproperty-alignment: AlignCenter;"
        )
        pet_header.addWidget(self.pet_avatar)

        pet_identity = QVBoxLayout()
        self.pet_profile_name = QLabel("-")
        self.pet_profile_name.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #244b3b;"
        )
        self.pet_profile_status = QLabel("Bình thường")
        self.pet_profile_status.setStyleSheet(
            "background: #edf7ee; color: #2d7d42; border-radius: 12px; padding: 5px 10px;"
        )
        pet_identity.addWidget(self.pet_profile_name)
        pet_identity.addWidget(self.pet_profile_status)
        pet_header.addLayout(pet_identity)
        pet_detail_layout.addLayout(pet_header)

        self.pet_profile_tabs = QTabWidget()
        self.pet_profile_tabs.addTab(self._build_pet_tab("overview"), "Overview")
        self.pet_profile_tabs.addTab(self._build_pet_tab("nutrition"), "Nutrition")
        self.pet_profile_tabs.addTab(self._build_pet_tab("health"), "Health")
        self.pet_profile_tabs.addTab(self._build_pet_tab("grooming"), "Grooming")
        pet_detail_layout.addWidget(self.pet_profile_tabs)
        detail_layout.addWidget(pet_detail_box, 3)
        detail_layout.addWidget(pets_box, 3)

        layout.addWidget(detail_widget)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.edit_customer_button = QPushButton("Chỉnh sửa")
        self.edit_customer_button.clicked.connect(self.edit_customer)
        buttons.addWidget(self.edit_customer_button)
        layout.addLayout(buttons)
        self.customers_table.currentCellChanged.connect(
            self._customer_selection_changed
        )
        return page

    def _build_reservations_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(
            QLabel(
                "Giữ chỗ chuyển động vật sang trạng thái đã đặt trước; "
                "tiền cọc phải được hoàn trước khi giải phóng."
            )
        )
        toolbar = QHBoxLayout()
        toolbar.addStretch()
        self.reserve_button = QPushButton("＋ Giữ chỗ", objectName="primaryButton")
        self.reserve_button.clicked.connect(self.create_reservation)
        self.refund_button = QPushButton("Hoàn tiền cọc")
        self.refund_button.clicked.connect(self.refund_deposit)
        self.release_button = QPushButton("Giải phóng chỗ")
        self.release_button.clicked.connect(self.release_reservation)
        for button in (self.reserve_button, self.refund_button, self.release_button):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.reservations_table = make_table(
            [
                "Động vật",
                "Khách hàng",
                "Điện thoại",
                "Hạn giữ",
                "Tiền cọc",
                "Đã hoàn",
                "Trạng thái",
            ]
        )
        self.reservations_table.currentCellChanged.connect(
            self._reservation_selection_changed
        )
        layout.addWidget(self.reservations_table)
        return page

    def _build_orders_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        toolbar = QHBoxLayout()
        toolbar.addWidget(
            QLabel(
                "Đơn có thể gồm động vật hoặc sản phẩm/combo; thanh toán đủ mới hoàn tất và xuất tồn."
            )
        )
        toolbar.addStretch()
        self.create_order_button = QPushButton(
            "+ Tạo đơn", objectName="primaryButton"
        )
        self.create_order_button.clicked.connect(self.create_order)
        self.create_product_order_button = QPushButton("+ Bán sản phẩm / combo")
        self.create_product_order_button.clicked.connect(self.create_product_order)
        self.payment_button = QPushButton("Ghi nhận thanh toán")
        self.payment_button.clicked.connect(self.add_payment)
        self.cancel_order_button = QPushButton("Hủy đơn chưa thanh toán")
        self.cancel_order_button.clicked.connect(self.cancel_order)
        for button in (
            self.create_order_button,
            self.create_product_order_button,
            self.payment_button,
            self.cancel_order_button,
        ):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.orders_table = make_table(
            [
                "Mã đơn",
                "Ngày",
                "Khách hàng",
                "Số dòng",
                "Tổng tiền",
                "Đã trả",
                "Còn lại",
                "Trạng thái",
            ]
        )
        self.orders_table.currentCellChanged.connect(self._order_selection_changed)
        layout.addWidget(self.orders_table, 3)
        self.order_items_table = make_table(
            ["Loại", "Mã SKU / động vật", "Tên hàng", "Loài / danh mục", "Số lượng", "Đơn giá"]
        )
        layout.addWidget(self.order_items_table, 2)
        self.payments_table = make_table(
            ["Ngày thanh toán", "Số tiền", "Phương thức", "Mã giao dịch", "Ghi chú"]
        )
        layout.addWidget(self.payments_table, 2)
        return page

    def _build_approvals_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(
            QLabel(
                "Nhân viên gửi yêu cầu để quản lý hoặc trưởng ca bán hàng duyệt. "
                "Người tạo yêu cầu không thể tự duyệt."
            )
        )
        self.approvals_table = make_table(
            [
                "Mã yêu cầu",
                "Người gửi",
                "Thao tác",
                "Chi tiết",
                "Trạng thái",
                "Thời điểm",
            ]
        )
        self.approvals_table.currentCellChanged.connect(
            self._approval_selection_changed
        )
        layout.addWidget(self.approvals_table)
        buttons = QHBoxLayout()
        self.approval_note = QLineEdit()
        self.approval_note.setPlaceholderText("Ghi chú quyết định (không bắt buộc)")
        buttons.addWidget(self.approval_note, 1)
        buttons.addStretch()
        self.refresh_approvals_button = QPushButton("Tải lại")
        self.refresh_approvals_button.clicked.connect(
            self.refresh_approval_requests
        )
        self.reject_approval_button = QPushButton("Từ chối")
        self.reject_approval_button.clicked.connect(
            lambda: self.review_selected_approval(False)
        )
        self.approve_button = QPushButton("Duyệt yêu cầu", objectName="primaryButton")
        self.approve_button.clicked.connect(
            lambda: self.review_selected_approval(True)
        )
        buttons.addWidget(self.refresh_approvals_button)
        buttons.addWidget(self.reject_approval_button)
        buttons.addWidget(self.approve_button)
        layout.addLayout(buttons)
        return page

    def set_manage_enabled(self, enabled: bool) -> None:
        self.set_access(enabled, enabled, enabled)

    def set_access(self, manage: bool, request: bool, approve: bool) -> None:
        self.manage_enabled = manage
        self.request_enabled = request
        self.approve_enabled = approve
        can_submit = manage or request
        for button in (
            self.add_customer_button,
            self.reserve_button,
            self.refund_button,
            self.release_button,
            self.create_order_button,
            self.create_product_order_button,
            self.payment_button,
            self.cancel_order_button,
        ):
            button.setVisible(can_submit)
        self.edit_customer_button.setVisible(can_submit)
        self.tabs.setTabVisible(
            self.tabs.indexOf(self.approvals_tab), request or approve
        )
        self.reject_approval_button.setVisible(approve)
        self.approve_button.setVisible(approve)
        self.approval_note.setVisible(approve)
        self.refresh_approvals_button.setVisible(request or approve)
        self.refresh_approval_requests()
        self._customer_selection_changed()
        self._reservation_selection_changed()
        self._order_selection_changed()
        self._approval_selection_changed()

    def refresh(self) -> None:
        self.refresh_customers()
        self.refresh_reservations()
        self.refresh_orders()
        self.refresh_approval_requests()

    @staticmethod
    def _selected_id(table: Any) -> int | None:
        row = table.currentRow()
        if row < 0 or table.item(row, 0) is None:
            return None
        return table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def selected_customer_id(self) -> int | None:
        return self._selected_id(self.customers_table)

    def selected_reservation_id(self) -> int | None:
        return self._selected_id(self.reservations_table)

    def selected_order_id(self) -> int | None:
        return self._selected_id(self.orders_table)

    def refresh_customers(self) -> None:
        customers = self.database.list_customers()
        selected_id = self.selected_customer_id()
        self.customers_table.setRowCount(len(customers))
        selected_row = -1
        for row, customer in enumerate(customers):
            set_cell(self.customers_table, row, 0, customer["customer_code"])
            self.customers_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, customer["id"]
            )
            if customer["id"] == selected_id:
                selected_row = row
            set_cell(self.customers_table, row, 1, customer["name"])
            set_cell(self.customers_table, row, 2, customer["phone"])
            set_cell(self.customers_table, row, 3, customer["email"])
            set_cell(self.customers_table, row, 4, customer["order_count"])
            set_cell(
                self.customers_table, row, 5, f"{customer['paid_total']:,.0f} ₫"
            )
        if selected_row >= 0:
            self.customers_table.selectRow(selected_row)
        elif customers:
            self.customers_table.selectRow(0)
        self._customer_selection_changed()

    def refresh_reservations(self) -> None:
        reservations = self.database.list_reservations()
        selected_id = self.selected_reservation_id()
        self.reservations_table.setRowCount(len(reservations))
        selected_row = -1
        for row, reservation in enumerate(reservations):
            set_cell(
                self.reservations_table,
                row,
                0,
                f"{reservation['animal_code']} — {reservation['animal_name']}",
            )
            self.reservations_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, reservation["id"]
            )
            if reservation["id"] == selected_id:
                selected_row = row
            set_cell(
                self.reservations_table,
                row,
                1,
                reservation["customer_name"],
            )
            set_cell(
                self.reservations_table,
                row,
                2,
                reservation["customer_phone"],
            )
            set_cell(self.reservations_table, row, 3, reservation["expires_at"])
            set_cell(
                self.reservations_table,
                row,
                4,
                f"{reservation['deposit_paid']:,.0f} ₫",
            )
            set_cell(
                self.reservations_table,
                row,
                5,
                f"{reservation['deposit_refunded']:,.0f} ₫",
            )
            set_cell(
                self.reservations_table,
                row,
                6,
                RESERVATION_STATUS_LABELS[reservation["status"]],
            )
        if selected_row >= 0:
            self.reservations_table.selectRow(selected_row)
        elif reservations:
            self.reservations_table.selectRow(0)
        self._reservation_selection_changed()

    def refresh_orders(self) -> None:
        orders = self.database.list_sales_orders()
        selected_id = self.selected_order_id()
        self.orders_table.setRowCount(len(orders))
        selected_row = -1
        for row, order in enumerate(orders):
            set_cell(self.orders_table, row, 0, order["order_code"])
            self.orders_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, order["id"]
            )
            if order["id"] == selected_id:
                selected_row = row
            set_cell(self.orders_table, row, 1, order["ordered_at"])
            set_cell(self.orders_table, row, 2, order["customer_name"])
            set_cell(self.orders_table, row, 3, order["item_count"])
            set_cell(self.orders_table, row, 4, f"{order['total_amount']:,.0f} ₫")
            set_cell(self.orders_table, row, 5, f"{order['paid_amount']:,.0f} ₫")
            balance = max(0, order["total_amount"] - order["paid_amount"])
            set_cell(self.orders_table, row, 6, f"{balance:,.0f} ₫")
            set_cell(
                self.orders_table, row, 7, ORDER_STATUS_LABELS[order["status"]]
            )
        if selected_row >= 0:
            self.orders_table.selectRow(selected_row)
        elif orders:
            self.orders_table.selectRow(0)
        self._order_selection_changed()

    def refresh_approval_requests(self) -> None:
        if not hasattr(self, "approvals_table"):
            return
        try:
            requests = self.database.list_sales_approval_requests()
        except PermissionError:
            self.approvals_table.setRowCount(0)
            return
        selected_id = self._selected_id(self.approvals_table)
        selected_row = -1
        labels = {
            "save_customer": "Hồ sơ khách hàng",
            "create_reservation": "Tạo lượt giữ chỗ",
            "release_reservation": "Giải phóng chỗ",
            "refund_reservation_deposit": "Hoàn tiền cọc",
            "create_sales_order": "Tạo đơn bán",
            "create_product_sales_order": "Bán sản phẩm / combo",
            "add_payment": "Ghi nhận thanh toán",
            "cancel_sales_order": "Hủy đơn",
        }
        self.approvals_table.setRowCount(len(requests))
        for row, request in enumerate(requests):
            payload = json.loads(request["payload_json"])
            values = payload.get("values", {})
            action_type = request["action_type"]
            if action_type == "save_customer":
                details = f"{values.get('name', '')} · {values.get('phone', '')}"
            elif action_type == "create_reservation":
                details = (
                    f"Khách #{values.get('customer_id')} · "
                    f"thú cưng #{values.get('animal_id')} · "
                    f"cọc {float(values.get('deposit', 0)):,.0f} ₫"
                )
            elif action_type == "release_reservation":
                details = f"Lượt giữ chỗ #{payload.get('reservation_id')}"
            elif action_type == "refund_reservation_deposit":
                details = (
                    f"Lượt giữ chỗ #{payload.get('reservation_id')} · "
                    f"hoàn {float(values.get('amount', 0)):,.0f} ₫"
                )
            elif action_type == "create_sales_order":
                details = (
                    f"{values.get('order_code', '')} · khách #{values.get('customer_id')} · "
                    f"{len(values.get('animal_ids', []))} thú cưng"
                )
            elif action_type == "create_product_sales_order":
                details = (
                    f"{values.get('order_code', '')} · khách #{values.get('customer_id')} · "
                    f"{len(values.get('product_lines', []))} SKU / "
                    f"{len(values.get('combo_lines', []))} combo"
                )
            elif action_type == "add_payment":
                details = (
                    f"Đơn #{payload.get('order_id')} · "
                    f"{float(values.get('amount', 0)):,.0f} ₫ · "
                    f"{values.get('method', '')}"
                )
            else:
                order = next(
                    (
                        item
                        for item in self.database.list_sales_orders()
                        if item["id"] == payload.get("order_id")
                    ),
                    None,
                )
                details = (
                    f"{order['order_code']} · {order['customer_name']} · "
                    f"{float(order['total_amount']):,.0f} ₫"
                    if order
                    else f"Đơn #{payload.get('order_id')}"
                )
            set_cell(self.approvals_table, row, 0, request["request_code"])
            self.approvals_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, request["id"]
            )
            if request["id"] == selected_id:
                selected_row = row
            set_cell(self.approvals_table, row, 1, request["requester"])
            set_cell(
                self.approvals_table,
                row,
                2,
                labels.get(action_type, action_type),
            )
            set_cell(self.approvals_table, row, 3, details)
            set_cell(self.approvals_table, row, 4, request["status"])
            set_cell(self.approvals_table, row, 5, request["requested_at"])
        if selected_row >= 0:
            self.approvals_table.selectRow(selected_row)
        elif requests:
            self.approvals_table.selectRow(0)
        self._approval_selection_changed()

    def _approval_selection_changed(self, *_: Any) -> None:
        request_id = self._selected_id(self.approvals_table)
        if request_id is None:
            self.approve_button.setEnabled(False)
            self.reject_approval_button.setEnabled(False)
            return
        request = next(
            (
                item for item in self.database.list_sales_approval_requests()
                if item["id"] == request_id
            ),
            None,
        )
        can_review = bool(
            self.approve_enabled
            and request is not None
            and request["status"] == "PENDING"
            and request["requester_id"] != self.database.actor_id
        )
        self.approve_button.setEnabled(can_review)
        self.reject_approval_button.setEnabled(can_review)

    def review_selected_approval(self, approve: bool) -> None:
        request_id = self._selected_id(self.approvals_table)
        if request_id is None:
            return
        try:
            self.database.review_sales_approval_request(
                request_id, approve, self.approval_note.text()
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self.approval_note.clear()
        self.refresh()

    def _submit_sales_action(
        self, action_type: str, payload: dict[str, Any]
    ) -> bool:
        try:
            result = self.database.submit_sales_action(action_type, payload)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return False
        if result["status"] == "PENDING":
            QMessageBox.information(
                self,
                "Đã gửi yêu cầu duyệt",
                f"Yêu cầu {result['request_code']} đang chờ quản lý hoặc trưởng ca duyệt.",
            )
        self.refresh()
        return True

    def _customer_selection_changed(self, *_: Any) -> None:
        self.edit_customer_button.setEnabled(
            (self.manage_enabled or self.request_enabled)
            and self.selected_customer_id() is not None
        )
        customer_id = self.selected_customer_id()
        if customer_id is None:
            self.customer_profile_name.setText("-")
            self.customer_profile_phone.setText("-")
            self.customer_profile_email.setText("-")
            self.customer_profile_address.setText("-")
            self.customer_profile_note.setText("-")
            self.customer_pets_table.setRowCount(0)
            return

        customer = self.database.get_customer(customer_id)
        if customer is None:
            return

        self.customer_profile_name.setText(str(customer["name"]))
        self.customer_profile_phone.setText(str(customer["phone"]) or "-")
        self.customer_profile_email.setText(str(customer["email"]) or "-")
        self.customer_profile_address.setText(str(customer["address"]) or "-")
        self.customer_profile_note.setText(str(customer["note"]) or "-")

        pets = self.database.list_pets(customer_id)
        self.customer_pets_table.setRowCount(len(pets))
        for row, pet in enumerate(pets):
            set_cell(self.customer_pets_table, row, 0, pet["name"])
            set_cell(self.customer_pets_table, row, 1, pet["species"])
            set_cell(self.customer_pets_table, row, 2, pet["breed_name"] or "-")
            birth_date = pet["birth_date"]
            if birth_date:
                age_text = birth_date
            else:
                age_text = "-"
            set_cell(self.customer_pets_table, row, 3, age_text)
            set_cell(self.customer_pets_table, row, 4, f"{pet['weight_kg']:.1f} kg" if pet["weight_kg"] is not None else "-")
            set_cell(self.customer_pets_table, row, 5, pet["health_status"] or "Bình thường")
        if pets:
            self.customer_pets_table.selectRow(0)
        self._selected_pet_changed()

    def _build_pet_tab(self, kind: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel("-")
        label.setWordWrap(True)
        setattr(self, f"pet_{kind}_summary", label)
        layout.addWidget(label)
        return tab

    def _selected_pet_changed(self, *_: Any) -> None:
        customer_id = self.selected_customer_id()
        if customer_id is None:
            self._clear_pet_profile()
            return
        pets = self.database.list_pets(customer_id)
        row = self.customer_pets_table.currentRow()
        if row < 0 or row >= len(pets):
            self._clear_pet_profile()
            return
        pet = pets[row]
        self.pet_profile_name.setText(f"{pet['name']} · {pet['species']}")
        self.pet_avatar.setText("🐶" if str(pet["species"]).lower().startswith("chó") else "🐱")

        health_status = pet["health_status"] or "Bình thường"
        self.pet_profile_status.setText(health_status)
        bg = "#edf7ee" if "bình thường" in health_status.lower() or "stable" in health_status.lower() else "#fff1d8"
        fg = "#2d7d42" if "bình thường" in health_status.lower() or "stable" in health_status.lower() else "#9b5f17"
        self.pet_profile_status.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 12px; padding: 5px 10px;"
        )

        age_text = pet["birth_date"] or "Chưa xác định"
        weight_text = f"{pet['weight_kg']:.1f} kg" if pet["weight_kg"] is not None else "Chưa cập nhật"
        environment_text = pet["environment_type"] or "Trong nhà"
        notes = pet["notes"] or "Không có ghi chú"
        self.pet_overview_summary.setText(
            f"Giống: {pet['breed_name'] or 'Chưa xác định'} | Tuổi: {age_text} | Cân nặng: {weight_text} | Môi trường: {environment_text} | Ghi chú: {notes}"
        )
        self.pet_nutrition_summary.setText(
            f"Khuyến nghị dinh dưỡng cho {pet['name']}: ưu tiên chế độ phù hợp với {pet['species']} và mức hoạt động {pet['activity_level'] or 'Trung bình'}. Cân nặng hiện tại {weight_text}."
        )
        self.pet_health_summary.setText(
            f"Tình trạng sức khỏe: {health_status}. Thân trạng {pet['body_condition'] or 'Bình thường'} và môi trường sống {environment_text}. Nên theo dõi định kỳ khi cần." 
        )
        self.pet_grooming_summary.setText(
            f"Chăm sóc cơ bản: chải lông, vệ sinh tai/mắt và kiểm tra da theo lịch. Mức độ hoạt động: {pet['activity_level'] or 'Trung bình'}, môi trường: {environment_text}."
        )

    def _clear_pet_profile(self) -> None:
        self.pet_profile_name.setText("-")
        self.pet_avatar.setText("🐾")
        self.pet_profile_status.setText("Bình thường")
        self.pet_profile_status.setStyleSheet(
            "background: #edf7ee; color: #2d7d42; border-radius: 12px; padding: 5px 10px;"
        )
        for key in ("overview", "nutrition", "health", "grooming"):
            summary = getattr(self, f"pet_{key}_summary", None)
            if summary is not None:
                summary.setText("-")

    def _reservation_selection_changed(self, *_: Any) -> None:
        reservation_id = self.selected_reservation_id()
        reservation = next(
            (
                row
                for row in self.database.list_reservations()
                if row["id"] == reservation_id
            ),
            None,
        )
        active = bool(reservation and reservation["status"] == "ACTIVE")
        can_submit = self.manage_enabled or self.request_enabled
        self.release_button.setEnabled(can_submit and active)
        self.refund_button.setEnabled(
            can_submit
            and active
            and self.database.get_reservation_balance(reservation_id) > 0
            if reservation_id is not None
            else False
        )

    def _order_selection_changed(self, *_: Any) -> None:
        order_id = self.selected_order_id()
        orders = self.database.list_sales_orders()
        order = next((item for item in orders if item["id"] == order_id), None)
        self.order_items_table.setRowCount(0)
        self.payments_table.setRowCount(0)
        self.payment_button.setEnabled(
            (self.manage_enabled or self.request_enabled)
            and order is not None
            and order["status"] in {"OPEN", "PARTIALLY_PAID"}
        )
        self.cancel_order_button.setEnabled(
            (self.manage_enabled or self.request_enabled)
            and order is not None
            and order["status"] == "OPEN"
        )
        if order_id is None:
            return
        animal_items = self.database.list_order_items(order_id)
        product_items = self.database.list_order_product_items(order_id)
        self.order_items_table.setRowCount(len(animal_items) + len(product_items))
        row = 0
        for item in animal_items:
            set_cell(self.order_items_table, row, 0, "Động vật")
            set_cell(self.order_items_table, row, 1, item["animal_code"])
            set_cell(self.order_items_table, row, 2, item["animal_name"])
            set_cell(self.order_items_table, row, 3, item["species"])
            set_cell(self.order_items_table, row, 4, "1")
            set_cell(self.order_items_table, row, 5, f"{item['unit_price']:,.0f} ₫")
            row += 1
        for item in product_items:
            set_cell(
                self.order_items_table,
                row,
                0,
                "Combo" if item["combo_id"] is not None else "Sản phẩm",
            )
            set_cell(self.order_items_table, row, 1, item["item_code"])
            set_cell(self.order_items_table, row, 2, item["item_name"])
            set_cell(self.order_items_table, row, 3, item["unit"])
            set_cell(self.order_items_table, row, 4, f"{item['quantity']:g}")
            set_cell(self.order_items_table, row, 5, f"{item['unit_price']:,.0f} ₫")
            row += 1
        payments = self.database.list_order_payments(order_id)
        self.payments_table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            set_cell(self.payments_table, row, 0, payment["paid_at"])
            set_cell(self.payments_table, row, 1, f"{payment['amount']:,.0f} ₫")
            set_cell(
                self.payments_table,
                row,
                2,
                PAYMENT_METHOD_LABELS[payment["method"]],
            )
            set_cell(self.payments_table, row, 3, payment["reference"])
            set_cell(self.payments_table, row, 4, payment["note"])

    def add_customer(self) -> None:
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_customer(dialog.values())

    def edit_customer(self) -> None:
        customer_id = self.selected_customer_id()
        customer = (
            self.database.get_customer(customer_id) if customer_id is not None else None
        )
        if customer is None:
            return
        dialog = CustomerDialog(self, customer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_customer(dialog.values(), customer_id)

    def _save_customer(
        self, values: dict[str, Any], customer_id: int | None = None
    ) -> None:
        self._submit_sales_action(
            "save_customer", {"values": values, "customer_id": customer_id}
        )

    def create_reservation(self) -> None:
        customers = self.database.list_customers()
        animals = [
            animal
            for animal in self.database.list_saleable_animals()
            if animal["status"] == "AVAILABLE"
        ]
        if not customers:
            QMessageBox.information(
                self, "Chưa có khách hàng", "Hãy thêm khách hàng trước khi giữ chỗ."
            )
            self.tabs.setCurrentWidget(self.customers_tab)
            return
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hiện không có động vật đang bán để giữ chỗ."
            )
            return
        dialog = ReservationDialog(self, customers, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._submit_sales_action(
            "create_reservation", {"values": dialog.values()}
        )

    def release_reservation(self) -> None:
        reservation_id = self.selected_reservation_id()
        if reservation_id is None:
            return
        answer = QMessageBox.question(
            self,
            "Giải phóng động vật",
            "Giải phóng chỗ và đưa động vật về trạng thái đang bán?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._submit_sales_action(
            "release_reservation", {"reservation_id": reservation_id}
        )

    def refund_deposit(self) -> None:
        reservation_id = self.selected_reservation_id()
        if reservation_id is None:
            return
        outstanding = self.database.get_reservation_balance(reservation_id)
        if outstanding <= 0:
            return
        dialog = RefundDepositDialog(self, reservation_id, outstanding)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        answer = QMessageBox.question(
            self,
            "Xác nhận hoàn cọc",
            "Xác nhận khoản hoàn tiền này đã được chi trả cho khách hàng?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._submit_sales_action(
            "refund_reservation_deposit",
            {"reservation_id": reservation_id, "values": dialog.values()},
        )

    def create_order(self) -> None:
        customers = self.database.list_customers()
        animals = self.database.list_saleable_animals()
        if not customers:
            QMessageBox.information(
                self, "Chưa có khách hàng", "Hãy thêm khách hàng trước khi tạo đơn."
            )
            self.tabs.setCurrentWidget(self.customers_tab)
            return
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hiện không có động vật đủ điều kiện để bán."
            )
            return
        dialog = SalesOrderDialog(self, customers, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._submit_sales_action(
            "create_sales_order", {"values": dialog.values()}
        )

    def create_product_order(self) -> None:
        customers = self.database.list_customers()
        if not customers:
            QMessageBox.information(
                self, "Chưa có khách hàng", "Hãy thêm khách hàng trước khi bán sản phẩm."
            )
            self.tabs.setCurrentWidget(self.customers_tab)
            return
        dialog = ProductSalesOrderDialog(self, self.database, customers)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._submit_sales_action(
            "create_product_sales_order", {"values": dialog.values()}
        )

    def add_payment(self) -> None:
        order_id = self.selected_order_id()
        if order_id is None:
            return
        try:
            balance = self.database.get_order_balance(order_id)
        except ValueError as error:
            self._show_error(error)
            return
        if balance <= 0:
            return
        dialog = PaymentDialog(self, balance)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._submit_sales_action(
            "add_payment", {"order_id": order_id, "values": dialog.values()}
        )

    def cancel_order(self) -> None:
        order_id = self.selected_order_id()
        if order_id is None:
            return
        answer = QMessageBox.question(
            self,
            "Hủy đơn hàng",
            "Hủy đơn chưa thanh toán và trả động vật về trạng thái đang bán?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._submit_sales_action("cancel_sales_order", {"order_id": order_id})

    def _show_error(self, error: Exception) -> None:
        detail = str(error)
        message = detail
        if isinstance(error, sqlite3.IntegrityError):
            if "customers.customer_code" in detail:
                message = "Mã khách hàng đã tồn tại."
            elif "sales_orders.order_code" in detail:
                message = "Mã đơn hàng đã tồn tại."
            elif "order_items.animal_id" in detail:
                message = "Động vật này đã nằm trong một đơn hàng khác."
        QMessageBox.warning(self, "Không thể thực hiện", message)
