import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QDialog,
    QDialogButtonBox,
)

from app.database import Database
from app.modules.sales.constants import PAYMENT_METHODS, PAYMENT_METHOD_LABELS
from app.ui.common import make_table, set_cell


def _set_row_id(table: Any, row: int, value: int) -> None:
    table.item(row, 0).setData(Qt.ItemDataRole.UserRole + 1, value)


def _selected_id(table: Any) -> int | None:
    row = table.currentRow()
    if row < 0 or table.item(row, 0) is None:
        return None
    value = table.item(row, 0).data(Qt.ItemDataRole.UserRole + 1)
    return int(value) if value is not None else None


class MembershipPlanDialog(QDialog):
    def __init__(self, parent: QWidget, plan: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật gói hội viên" if plan else "Tạo gói hội viên")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.description = QLineEdit()
        self.duration = QSpinBox()
        self.duration.setRange(1, 36500)
        self.duration.setSuffix(" ngày")
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1_000_000_000)
        self.price.setDecimals(0)
        self.price.setSuffix(" VND")
        self.discount = QDoubleSpinBox()
        self.discount.setRange(0, 100)
        self.discount.setSuffix(" %")
        self.points = QDoubleSpinBox()
        self.points.setRange(0, 1000)
        self.max_pets = QSpinBox()
        self.max_pets.setRange(1, 100)
        self.billing_mode = QComboBox()
        self.billing_mode.addItem("Trả trước theo lượt", "PREPAID_VISITS")
        self.billing_mode.addItem("Giảm giá hội viên", "MEMBER_DISCOUNT")
        self.billing_mode.addItem("Định kỳ, lập bill thủ công", "RECURRING")
        self.included_visits = QSpinBox()
        self.included_visits.setRange(0, 1000)
        self.service_category = QLineEdit()
        self.service_category.setPlaceholderText("Ví dụ: BATH hoặc để trống")
        self.benefits = QTextEdit()
        self.benefits.setMaximumHeight(80)
        self.active = QCheckBox("Đang hoạt động")
        self.active.setChecked(True)
        for label, widget in (
            ("Mã gói *", self.code),
            ("Tên gói *", self.name),
            ("Mô tả", self.description),
            ("Thời hạn", self.duration),
            ("Giá", self.price),
            ("Giảm giá mua hàng", self.discount),
            ("Tỷ lệ tích điểm", self.points),
            ("Số thú cưng tối đa", self.max_pets),
            ("Kiểu quyền lợi", self.billing_mode),
            ("Số lượt trả trước", self.included_visits),
            ("Loại dịch vụ áp dụng", self.service_category),
            ("Quyền lợi", self.benefits),
            ("Trạng thái", self.active),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if plan:
            self.code.setText(plan["code"])
            self.name.setText(plan["name"])
            self.description.setText(plan["description"])
            self.duration.setValue(plan["duration_days"])
            self.price.setValue(plan["price"])
            self.discount.setValue(plan["discount_percent"])
            self.points.setValue(plan["points_rate"])
            self.max_pets.setValue(plan["max_pets"])
            mode_index = self.billing_mode.findData(plan["billing_mode"])
            if mode_index >= 0:
                self.billing_mode.setCurrentIndex(mode_index)
            self.included_visits.setValue(plan["included_visits"])
            self.service_category.setText(plan["service_category"])
            self.benefits.setPlainText(plan["benefits"])
            self.active.setChecked(bool(plan["is_active"]))

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã và tên gói là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "code": self.code.text(),
            "name": self.name.text(),
            "description": self.description.text(),
            "duration_days": self.duration.value(),
            "price": self.price.value(),
            "discount_percent": self.discount.value(),
            "points_rate": self.points.value(),
            "max_pets": self.max_pets.value(),
            "billing_mode": self.billing_mode.currentData(),
            "included_visits": self.included_visits.value(),
            "service_category": self.service_category.text(),
            "benefits": self.benefits.toPlainText(),
            "is_active": self.active.isChecked(),
        }


class MembershipPaymentDialog(QDialog):
    def __init__(self, parent: QWidget, bill: sqlite3.Row) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Thanh toán {bill['bill_number']}")
        layout = QVBoxLayout(self)
        self.balance = round(float(bill["total_amount"]) - float(bill["amount_paid"]), 2)
        layout.addWidget(
            QLabel(f"Còn phải thu: {self.balance:,.0f} VND\n"
                   "Chỉ xác nhận sau khi nhân viên kiểm tra tiền đã nhận.")
        )
        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, max(self.balance, 0.01))
        self.amount.setDecimals(0)
        self.amount.setValue(self.balance)
        self.method = QComboBox()
        self.method.addItems(PAYMENT_METHODS)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Số tiền", self.amount)
        form.addRow("Phương thức", self.method)
        form.addRow("Mã tham chiếu", self.reference)
        form.addRow("Ghi chú", self.note)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "amount": self.amount.value(),
            "method": self.method.currentText(),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }


class MembershipPage(QWidget):
    def __init__(self, database: Database, can_manage: bool = True) -> None:
        super().__init__()
        self.database = database
        self.can_manage = can_manage
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Hội viên & tài chính", objectName="pageTitle"))
        self.notice = QLabel(
            "Quản trị hội viên nội bộ · bill và thanh toán được lưu sổ; "
            "chưa tích hợp ngân hàng, QR thanh toán hoặc hóa đơn điện tử."
        )
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm khách hàng, mã hội viên hoặc bill")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search, 1)
        self.add_plan_button = QPushButton("＋ Tạo gói")
        self.add_plan_button.clicked.connect(self.add_plan)
        self.edit_plan_button = QPushButton("Sửa gói")
        self.edit_plan_button.clicked.connect(self.edit_plan)
        self.enroll_button = QPushButton("＋ Cấp hội viên")
        self.enroll_button.setObjectName("primaryButton")
        self.enroll_button.clicked.connect(self.enroll)
        self.renew_button = QPushButton("Tạo bill gia hạn")
        self.renew_button.clicked.connect(self.renew)
        self.pay_button = QPushButton("Ghi nhận thanh toán")
        self.pay_button.clicked.connect(self.record_payment)
        self.payment_history_button = QPushButton("Lịch sử thanh toán")
        self.payment_history_button.clicked.connect(self.payment_history)
        for button in (
            self.add_plan_button,
            self.edit_plan_button,
            self.enroll_button,
            self.renew_button,
            self.pay_button,
            self.payment_history_button,
        ):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)

        tabs = QTabWidget()
        self.plans_table = make_table(
            ["Mã gói", "Tên gói", "Thời hạn", "Giá", "Kiểu quyền lợi",
             "Lượt", "Giảm giá", "Thú cưng", "Trạng thái"]
        )
        self.members_table = make_table(
            ["Mã hội viên", "Khách hàng", "Gói", "Thẻ", "Bắt đầu", "Hết hạn", "Trạng thái", "Bills"]
        )
        self.bills_table = make_table(
            ["Mã bill", "Ngày", "Khách hàng", "Loại", "Tổng", "Đã trả", "Còn lại", "Trạng thái"]
        )
        tabs.addTab(self.members_table, "Hội viên & thẻ")
        tabs.addTab(self.bills_table, "Bill & thanh toán")
        tabs.addTab(self.plans_table, "Cấu hình gói")
        layout.addWidget(tabs, 1)
        for button in (
            self.add_plan_button,
            self.edit_plan_button,
            self.enroll_button,
            self.renew_button,
            self.pay_button,
        ):
            button.setEnabled(can_manage)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        for button in (
            self.add_plan_button,
            self.edit_plan_button,
            self.enroll_button,
            self.renew_button,
            self.pay_button,
        ):
            button.setEnabled(enabled)

    def refresh(self) -> None:
        term = self.search.text().strip()
        try:
            plans = self.database.list_membership_plans()
            memberships = self.database.list_memberships(term)
            bills = self.database.list_membership_bills(term)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.notice.setText(f"Không thể tải dữ liệu hội viên: {error}")
            return
        self.plans_table.setRowCount(len(plans))
        for row, plan in enumerate(plans):
            values = (
                plan["code"], plan["name"], f"{plan['duration_days']} ngày",
                f"{plan['price']:,.0f} VND",
                {
                    "PREPAID_VISITS": "Trả trước",
                    "MEMBER_DISCOUNT": "Giảm giá",
                    "RECURRING": "Định kỳ",
                }.get(plan["billing_mode"], plan["billing_mode"]),
                str(plan["included_visits"]),
                f"{plan['discount_percent']:g}%",
                str(plan["max_pets"]), "Đang hoạt động" if plan["is_active"] else "Ngừng",
            )
            for column, value in enumerate(values):
                set_cell(self.plans_table, row, column, value)
            _set_row_id(self.plans_table, row, plan["id"])
        self.members_table.setRowCount(len(memberships))
        for row, member in enumerate(memberships):
            values = (
                member["membership_code"], member["customer_name"], member["plan_name"],
                member["card_number"] or "—", member["start_date"], member["end_date"],
                member["display_status"], member["bill_count"],
            )
            for column, value in enumerate(values):
                set_cell(self.members_table, row, column, value)
            _set_row_id(self.members_table, row, member["id"])
        self.bills_table.setRowCount(len(bills))
        for row, bill in enumerate(bills):
            balance = max(0, round(bill["total_amount"] - bill["amount_paid"], 2))
            values = (
                bill["bill_number"], bill["issued_at"], bill["customer_name"],
                {
                    "RENEWAL": "Gia hạn",
                    "OTHER": "Dịch vụ",
                    "MEMBERSHIP": "Hội viên",
                }.get(bill["bill_type"], bill["bill_type"]),
                f"{bill['total_amount']:,.0f}", f"{bill['amount_paid']:,.0f}",
                f"{balance:,.0f}", bill["status"],
            )
            for column, value in enumerate(values):
                set_cell(self.bills_table, row, column, value)
            _set_row_id(self.bills_table, row, bill["id"])

    def add_plan(self) -> None:
        dialog = MembershipPlanDialog(self)
        if dialog.exec():
            self._save_plan(dialog.values())

    def edit_plan(self) -> None:
        plan_id = _selected_id(self.plans_table)
        if plan_id is None:
            QMessageBox.information(self, "Chọn gói", "Hãy chọn gói cần sửa.")
            return
        plan = next(
            (item for item in self.database.list_membership_plans() if item["id"] == plan_id),
            None,
        )
        if plan is None:
            QMessageBox.warning(self, "Không tìm thấy", "Gói hội viên không còn tồn tại.")
            return
        dialog = MembershipPlanDialog(self, plan)
        if dialog.exec():
            self._save_plan(dialog.values(), plan_id)

    def _save_plan(self, values: dict[str, Any], plan_id: int | None = None) -> None:
        try:
            self.database.save_membership_plan(values, plan_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lưu gói", str(error))
            return
        self.refresh()

    def enroll(self) -> None:
        customers = self.database.list_customers()
        plans = self.database.list_membership_plans(include_inactive=False)
        if not customers:
            QMessageBox.information(self, "Chưa có khách hàng", "Hãy tạo hồ sơ khách hàng trước.")
            return
        if not plans:
            QMessageBox.information(self, "Chưa có gói", "Hãy tạo một gói hội viên trước.")
            return
        customer_labels = [f"{item['customer_code']} · {item['name']} · {item['phone']}" for item in customers]
        customer, accepted = QInputDialog.getItem(
            self, "Cấp hội viên", "Khách hàng", customer_labels, 0, False
        )
        if not accepted:
            return
        plan_labels = [f"{item['code']} · {item['name']} · {item['price']:,.0f} VND" for item in plans]
        plan, accepted = QInputDialog.getItem(
            self, "Cấp hội viên", "Gói hội viên", plan_labels, 0, False
        )
        if not accepted:
            return
        try:
            membership_id = self.database.create_membership(
                int(customers[customer_labels.index(customer)]["id"]),
                int(plans[plan_labels.index(plan)]["id"]),
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể cấp hội viên", str(error))
            return
        self.refresh()
        QMessageBox.information(
            self, "Đã tạo hội viên", f"Đã tạo hội viên và bill liên kết (ID {membership_id})."
        )

    def renew(self) -> None:
        membership_id = _selected_id(self.members_table)
        if membership_id is None:
            QMessageBox.information(self, "Chọn hội viên", "Hãy chọn hội viên cần gia hạn.")
            return
        try:
            bill_id = self.database.create_membership_renewal(membership_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tạo bill gia hạn", str(error))
            return
        self.refresh()
        QMessageBox.information(
            self, "Đã tạo bill", f"Bill gia hạn ID {bill_id} đang chờ thanh toán."
        )

    def record_payment(self) -> None:
        bill_id = _selected_id(self.bills_table)
        if bill_id is None:
            QMessageBox.information(self, "Chọn bill", "Hãy chọn bill cần thanh toán.")
            return
        bill = next(
            (item for item in self.database.list_membership_bills(self.search.text()) if item["id"] == bill_id),
            None,
        )
        if bill is None:
            QMessageBox.warning(self, "Không tìm thấy", "Bill không còn tồn tại.")
            return
        dialog = MembershipPaymentDialog(self, bill)
        if dialog.exec():
            try:
                self.database.add_membership_bill_payment(bill_id, dialog.values())
            except (sqlite3.Error, ValueError, PermissionError) as error:
                QMessageBox.warning(self, "Không thể ghi nhận thanh toán", str(error))
                return
            self.refresh()

    def payment_history(self) -> None:
        bill_id = _selected_id(self.bills_table)
        if bill_id is None:
            QMessageBox.information(self, "Chọn bill", "Hãy chọn bill để xem lịch sử.")
            return
        try:
            payments = self.database.list_membership_bill_payments(bill_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tải lịch sử", str(error))
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Lịch sử thanh toán")
        dialog.resize(650, 360)
        layout = QVBoxLayout(dialog)
        table = make_table(["Mã thanh toán", "Ngày", "Phương thức", "Số tiền", "Tham chiếu"])
        table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            values = (
                payment["payment_code"], payment["paid_at"],
                PAYMENT_METHOD_LABELS.get(payment["payment_method"], payment["payment_method"]),
                f"{payment['amount']:,.0f} VND", payment["reference"],
            )
            for column, value in enumerate(values):
                set_cell(table, row, column, value)
        layout.addWidget(table)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()
