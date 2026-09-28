import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
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
        self.tabs.addTab(self.customers_tab, "Khách hàng")
        self.tabs.addTab(self.reservations_tab, "Đặt trước")
        self.tabs.addTab(self.orders_tab, "Đơn hàng & thanh toán")
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
            QLabel("Động vật chỉ được chuyển sang “Đã bán” khi thanh toán đủ.")
        )
        toolbar.addStretch()
        self.create_order_button = QPushButton(
            "+ Tạo đơn", objectName="primaryButton"
        )
        self.create_order_button.clicked.connect(self.create_order)
        self.payment_button = QPushButton("Ghi nhận thanh toán")
        self.payment_button.clicked.connect(self.add_payment)
        self.cancel_order_button = QPushButton("Hủy đơn chưa thanh toán")
        self.cancel_order_button.clicked.connect(self.cancel_order)
        for button in (
            self.create_order_button,
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
                "Số con",
                "Tổng tiền",
                "Đã trả",
                "Còn lại",
                "Trạng thái",
            ]
        )
        self.orders_table.currentCellChanged.connect(self._order_selection_changed)
        layout.addWidget(self.orders_table, 3)
        self.order_items_table = make_table(
            ["Mã động vật", "Tên", "Loài", "Đơn giá"]
        )
        layout.addWidget(self.order_items_table, 2)
        self.payments_table = make_table(
            ["Ngày thanh toán", "Số tiền", "Phương thức", "Mã giao dịch", "Ghi chú"]
        )
        layout.addWidget(self.payments_table, 2)
        return page

    def set_manage_enabled(self, enabled: bool) -> None:
        self.manage_enabled = enabled
        for button in (
            self.add_customer_button,
            self.edit_customer_button,
            self.reserve_button,
            self.refund_button,
            self.release_button,
            self.create_order_button,
            self.payment_button,
            self.cancel_order_button,
        ):
            button.setVisible(enabled)

    def refresh(self) -> None:
        self.refresh_customers()
        self.refresh_reservations()
        self.refresh_orders()

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

    def _customer_selection_changed(self, *_: Any) -> None:
        self.edit_customer_button.setEnabled(
            self.manage_enabled and self.selected_customer_id() is not None
        )

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
        self.release_button.setEnabled(self.manage_enabled and active)
        self.refund_button.setEnabled(
            self.manage_enabled
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
            self.manage_enabled
            and order is not None
            and order["status"] in {"OPEN", "PARTIALLY_PAID"}
        )
        self.cancel_order_button.setEnabled(
            self.manage_enabled and order is not None and order["status"] == "OPEN"
        )
        if order_id is None:
            return
        for row, item in enumerate(self.database.list_order_items(order_id)):
            self.order_items_table.insertRow(row)
            set_cell(self.order_items_table, row, 0, item["animal_code"])
            set_cell(self.order_items_table, row, 1, item["animal_name"])
            set_cell(self.order_items_table, row, 2, item["species"])
            set_cell(self.order_items_table, row, 3, f"{item['unit_price']:,.0f} ₫")
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
        try:
            self.database.save_customer(values, customer_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_customers()

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
        try:
            self.database.create_reservation(dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_reservations()
        self.refresh_orders()

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
        try:
            self.database.release_reservation(reservation_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_reservations()

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
        try:
            self.database.refund_reservation_deposit(
                reservation_id, dialog.values()
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_reservations()

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
        try:
            self.database.create_sales_order(dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_orders()
        self.refresh_reservations()

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
        try:
            self.database.add_payment(order_id, dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_orders()
        self.refresh_customers()

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
        try:
            self.database.cancel_sales_order(order_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_orders()

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
