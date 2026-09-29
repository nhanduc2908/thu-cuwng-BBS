import sqlite3
from typing import Any

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
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
)

from app.database import Database
from app.modules.services.constants import SERVICE_CATEGORIES, SERVICE_CATEGORY_LABELS
from app.ui.common import make_table, set_cell


STATUS_LABELS = {
    "SCHEDULED": "Đã đặt lịch",
    "CHECKED_IN": "Đã tiếp nhận",
    "IN_PROGRESS": "Đang thực hiện",
    "COMPLETED": "Hoàn thành",
    "CANCELLED": "Đã hủy",
    "NO_SHOW": "Không đến",
}
COAT_OPTIONS = ("Không rõ", "Ngắn", "Dài", "Hai lớp", "Xoăn", "Dày")


def _row_id(table: Any) -> int | None:
    row = table.currentRow()
    item = table.item(row, 0) if row >= 0 else None
    if item is None:
        return None
    value = item.data(Qt.ItemDataRole.UserRole + 1)
    return int(value) if value is not None else None


def _store_id(table: Any, row: int, value: int) -> None:
    table.item(row, 0).setData(Qt.ItemDataRole.UserRole + 1, value)


class ServicePackageDialog(QDialog):
    def __init__(self, parent: QWidget, package: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.is_demo = bool(package and package["is_demo"])
        self.setWindowTitle("Sửa gói dịch vụ" if package else "Tạo gói dịch vụ")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.category = QComboBox()
        for key in sorted(SERVICE_CATEGORIES):
            self.category.addItem(SERVICE_CATEGORY_LABELS[key], key)
        self.description = QTextEdit()
        self.description.setMaximumHeight(70)
        self.species = QLineEdit("Chó, Mèo")
        self.coats = QLineEdit("ANY")
        self.min_weight = self._number_box(0, 250)
        self.max_weight = self._number_box(0, 250)
        self.max_weight.setSpecialValueText("Không giới hạn")
        self.duration = QSpinBox()
        self.duration.setRange(5, 1440)
        self.duration.setSuffix(" phút")
        self.price = self._number_box(0, 1_000_000_000)
        self.member_price = self._number_box(0, 1_000_000_000)
        self.member_price_enabled = QCheckBox("Có giá riêng")
        self.member_price_enabled.toggled.connect(self.member_price.setEnabled)
        self.member_price.setEnabled(False)
        member_price_widget = QWidget()
        member_price_layout = QHBoxLayout(member_price_widget)
        member_price_layout.setContentsMargins(0, 0, 0, 0)
        member_price_layout.addWidget(self.member_price_enabled)
        member_price_layout.addWidget(self.member_price, 1)
        self.included_weight = self._number_box(0, 250)
        self.per_kg = self._number_box(0, 1_000_000)
        self.coat_fee = self._number_box(0, 1_000_000)
        self.active = QCheckBox("Đang hoạt động")
        self.active.setChecked(True)
        for label, widget in (
            ("Mã gói *", self.code),
            ("Tên gói *", self.name),
            ("Loại", self.category),
            ("Mô tả", self.description),
            ("Loài áp dụng", self.species),
            ("Loại lông tính phụ phí", self.coats),
            ("Cân nặng tối thiểu (kg)", self.min_weight),
            ("Cân nặng tối đa (kg)", self.max_weight),
            ("Thời lượng", self.duration),
            ("Giá niêm yết (VND)", self.price),
            ("Giá hội viên (VND)", member_price_widget),
            ("Cân nặng đã gồm (kg)", self.included_weight),
            ("Phụ phí mỗi kg vượt ngưỡng (VND)", self.per_kg),
            ("Phụ phí lông dài/dày (VND)", self.coat_fee),
            ("Trạng thái", self.active),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if package:
            self.code.setText(package["code"])
            self.name.setText(package["name"])
            self.category.setCurrentIndex(
                max(0, self.category.findData(package["category"]))
            )
            self.description.setPlainText(package["description"])
            self.species.setText(package["species"])
            self.coats.setText(package["coat_types"])
            self.min_weight.setValue(package["min_weight"])
            self.max_weight.setValue(package["max_weight"] or 0)
            self.duration.setValue(package["duration_minutes"])
            self.price.setValue(package["list_price"])
            self.member_price_enabled.setChecked(package["member_price"] is not None)
            if package["member_price"] is not None:
                self.member_price.setValue(package["member_price"])
            self.included_weight.setValue(package["included_weight_kg"])
            self.per_kg.setValue(package["surcharge_per_kg"])
            self.coat_fee.setValue(package["coat_surcharge"])
            self.active.setChecked(bool(package["is_active"]))

    @staticmethod
    def _number_box(minimum: float, maximum: float) -> QDoubleSpinBox:
        widget = QDoubleSpinBox()
        widget.setRange(minimum, maximum)
        widget.setDecimals(2)
        widget.setSingleStep(0.5)
        return widget

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã và tên gói là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "code": self.code.text(),
            "name": self.name.text(),
            "category": self.category.currentData(),
            "description": self.description.toPlainText(),
            "species": self.species.text(),
            "coat_types": self.coats.text(),
            "min_weight": self.min_weight.value(),
            "max_weight": self.max_weight.value() or None,
            "duration_minutes": self.duration.value(),
            "list_price": self.price.value(),
            "member_price": (
                self.member_price.value()
                if self.member_price_enabled.isChecked()
                else None
            ),
            "included_weight_kg": self.included_weight.value(),
            "surcharge_per_kg": self.per_kg.value(),
            "coat_surcharge": self.coat_fee.value(),
            "is_demo": self.is_demo,
            "is_active": self.active.isChecked(),
        }


class ServiceBookingDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        database: Database,
        packages: list[sqlite3.Row],
        customers: list[sqlite3.Row],
        staff: list[str],
    ) -> None:
        super().__init__(parent)
        self.database = database
        self.packages = packages
        self.customers = customers
        self.setWindowTitle("Đặt lịch dịch vụ")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.customer = QComboBox()
        for item in customers:
            self.customer.addItem(
                f"{item['customer_code']} · {item['name']} · {item['phone']}",
                item["id"],
            )
        self.package = QComboBox()
        for item in packages:
            self.package.addItem(
                f"{item['name']} · {item['list_price']:,.0f} VND",
                item["id"],
            )
        self.pet_name = QLineEdit()
        self.species = QComboBox()
        self.species.addItems(["Chó", "Mèo", "Khác"])
        self.weight = QDoubleSpinBox()
        self.weight.setRange(0, 250)
        self.weight.setDecimals(2)
        self.weight.setSpecialValueText("Chưa cân")
        self.coat = QComboBox()
        self.coat.addItems(COAT_OPTIONS)
        self.scheduled = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        self.scheduled.setCalendarPopup(True)
        self.scheduled.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.staff = QComboBox()
        self.staff.setEditable(True)
        self.staff.addItem("Chưa phân công")
        self.staff.addItems(staff)
        self.membership = QComboBox()
        self.membership.addItem("Không dùng hội viên", None)
        self.note = QLineEdit()
        self.quote_label = QLabel()
        self.quote_label.setWordWrap(True)
        for label, widget in (
            ("Khách hàng *", self.customer),
            ("Gói dịch vụ *", self.package),
            ("Tên thú cưng *", self.pet_name),
            ("Loài *", self.species),
            ("Cân nặng (kg)", self.weight),
            ("Loại lông", self.coat),
            ("Ngày giờ hẹn *", self.scheduled),
            ("Nhân viên", self.staff),
            ("Gói hội viên", self.membership),
            ("Ghi chú", self.note),
            ("Tạm tính", self.quote_label),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.customer.currentIndexChanged.connect(self._load_memberships)
        self.package.currentIndexChanged.connect(self._update_quote)
        self.species.currentTextChanged.connect(self._update_quote)
        self.weight.valueChanged.connect(self._update_quote)
        self.coat.currentTextChanged.connect(self._update_quote)
        self.membership.currentIndexChanged.connect(self._update_quote)
        self._load_memberships()

    def _load_memberships(self) -> None:
        self.membership.blockSignals(True)
        self.membership.clear()
        self.membership.addItem("Không dùng hội viên", None)
        customer_id = self.customer.currentData()
        if customer_id is not None:
            try:
                memberships = self.database.list_customer_service_memberships(
                    int(customer_id)
                )
            except (sqlite3.Error, ValueError, PermissionError) as error:
                QMessageBox.warning(self, "Không tải được hội viên", str(error))
                memberships = []
            for member in memberships:
                detail = member["plan_name"]
                if member["billing_mode"] == "PREPAID_VISITS":
                    detail += f" · còn {member['remaining_visits']} lượt"
                self.membership.addItem(detail, member["id"])
        self.membership.blockSignals(False)
        self._update_quote()

    def _update_quote(self) -> None:
        package_id = self.package.currentData()
        if package_id is None:
            return
        weight = self.weight.value() or None
        membership_id = self.membership.currentData()
        try:
            quote = self.database.get_service_quote(
                int(package_id),
                self.species.currentText(),
                weight,
                self.coat.currentText(),
                int(membership_id) if membership_id is not None else None,
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.quote_label.setText(f"Chưa tính được giá: {error}")
            return
        self.quote_label.setText(
            f"Giá gốc {quote['base_price']:,.0f} + phụ phí "
            f"{quote['surcharge']:,.0f} - ưu đãi {quote['discount']:,.0f} "
            f"= {quote['total_price']:,.0f} VND"
        )

    def values(self) -> dict[str, Any]:
        assigned_staff = self.staff.currentText().strip()
        if assigned_staff == "Chưa phân công":
            assigned_staff = ""
        return {
            "customer_id": self.customer.currentData(),
            "package_id": self.package.currentData(),
            "pet_name": self.pet_name.text(),
            "species": self.species.currentText(),
            "weight_kg": self.weight.value() or None,
            "coat_type": self.coat.currentText(),
            "scheduled_at": self.scheduled.dateTime().toString(Qt.DateFormat.ISODate),
            "assigned_staff": assigned_staff,
            "membership_id": self.membership.currentData(),
            "note": self.note.text(),
        }


class ServicesPage(QWidget):
    def __init__(
        self,
        database: Database,
        can_manage: bool,
        can_manage_catalog: bool,
    ) -> None:
        super().__init__()
        self.database = database
        self.can_manage = can_manage
        self.notice = QLabel()
        self.notice.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        header = QHBoxLayout()
        header.addWidget(QLabel("Dịch vụ & lịch hẹn", objectName="pageTitle"))
        header.addStretch()
        self.book_button = QPushButton("＋ Đặt lịch", objectName="primaryButton")
        self.book_button.clicked.connect(self.book)
        header.addWidget(self.book_button)
        layout.addLayout(header)
        layout.addWidget(self.notice)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm gói, lịch hẹn, thú cưng hoặc khách hàng")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search, 1)
        self.add_package_button = QPushButton("＋ Tạo gói")
        self.add_package_button.clicked.connect(self.add_package)
        self.edit_package_button = QPushButton("Sửa gói")
        self.edit_package_button.clicked.connect(self.edit_package)
        self.status_button = QPushButton("Cập nhật trạng thái")
        self.status_button.clicked.connect(self.update_status)
        self.reschedule_button = QPushButton("Dời lịch")
        self.reschedule_button.clicked.connect(self.reschedule)
        for button in (
            self.add_package_button,
            self.edit_package_button,
            self.status_button,
            self.reschedule_button,
        ):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        tabs = QTabWidget()
        self.packages_table = make_table(
            ["Mã", "Tên gói", "Loại", "Loài", "Thời lượng", "Giá", "Hội viên", "Trạng thái"]
        )
        self.appointments_table = make_table(
            ["Mã lịch", "Ngày giờ", "Khách hàng", "Thú cưng", "Dịch vụ", "Nhân viên", "Tổng", "Trạng thái", "Bill"]
        )
        tabs.addTab(self.appointments_table, "Lịch hẹn")
        tabs.addTab(self.packages_table, "Danh mục gói")
        layout.addWidget(tabs, 1)
        self.book_button.setEnabled(can_manage)
        self.status_button.setEnabled(can_manage)
        self.reschedule_button.setEnabled(can_manage)
        self.add_package_button.setEnabled(can_manage_catalog)
        self.edit_package_button.setEnabled(can_manage_catalog)
        self.refresh()

    def refresh(self) -> None:
        search = self.search.text().strip()
        try:
            packages = self.database.list_service_packages(search)
            appointments = self.database.list_service_appointments(search)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.notice.setText(f"Không thể tải dịch vụ và lịch hẹn: {error}")
            return
        self.notice.setText(
            "280 gói demo tham khảo; mức giá/phụ phí cần được cửa hàng xác nhận và cấu hình."
        )
        self.packages_table.setRowCount(len(packages))
        for row, package in enumerate(packages):
            values = (
                package["code"],
                package["name"],
                SERVICE_CATEGORY_LABELS.get(package["category"], package["category"]),
                package["species"],
                f"{package['duration_minutes']} phút",
                f"{package['list_price']:,.0f} VND",
                "—"
                if package["member_price"] is None
                else f"{package['member_price']:,.0f} VND",
                "Đang hoạt động" if package["is_active"] else "Ngừng",
            )
            for column, value in enumerate(values):
                set_cell(self.packages_table, row, column, value)
            _store_id(self.packages_table, row, package["id"])
        self.appointments_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            bill = appointment["bill_number"]
            if not bill and appointment["membership_mode"] == "PREPAID_VISITS":
                bill = (
                    "Đã dùng lượt"
                    if appointment["status"] == "COMPLETED"
                    else "Đã trả lượt giữ"
                    if appointment["status"] in {"CANCELLED", "NO_SHOW"}
                    else "Đang giữ lượt"
                )
            elif not bill:
                bill = "Chưa lập bill"
            values = (
                appointment["appointment_code"],
                appointment["scheduled_at"],
                appointment["customer_name"],
                f"{appointment['pet_name']} ({appointment['species']})",
                appointment["package_name"],
                appointment["assigned_staff"] or "Chưa phân công",
                f"{appointment['total_price']:,.0f} VND",
                STATUS_LABELS.get(appointment["status"], appointment["status"]),
                bill,
            )
            for column, value in enumerate(values):
                set_cell(self.appointments_table, row, column, value)
            _store_id(self.appointments_table, row, appointment["id"])

    def add_package(self) -> None:
        dialog = ServicePackageDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_package(dialog.values())

    def edit_package(self) -> None:
        package_id = _row_id(self.packages_table)
        if package_id is None:
            QMessageBox.information(self, "Chọn gói", "Hãy chọn gói cần sửa.")
            return
        package = next(
            (
                item
                for item in self.database.list_service_packages()
                if item["id"] == package_id
            ),
            None,
        )
        if package is None:
            QMessageBox.warning(self, "Không tìm thấy", "Gói dịch vụ không còn tồn tại.")
            return
        dialog = ServicePackageDialog(self, package)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_package(dialog.values(), package_id)

    def _save_package(
        self, values: dict[str, Any], package_id: int | None = None
    ) -> None:
        try:
            self.database.save_service_package(values, package_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lưu gói", str(error))
            return
        self.refresh()

    def book(self) -> None:
        try:
            packages = self.database.list_service_packages(include_inactive=False)
            customers = self.database.list_customers()
            staff = self.database.list_service_staff()
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể đặt lịch", str(error))
            return
        if not packages or not customers:
            QMessageBox.information(
                self,
                "Thiếu dữ liệu",
                "Cần có ít nhất một gói dịch vụ đang hoạt động và một khách hàng.",
            )
            return
        dialog = ServiceBookingDialog(self, self.database, packages, customers, staff)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            appointment_id = self.database.create_service_appointment(dialog.values())
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể đặt lịch", str(error))
            return
        self.refresh()
        QMessageBox.information(
            self, "Đã đặt lịch", f"Đã tạo lịch hẹn (ID {appointment_id})."
        )

    def update_status(self) -> None:
        appointment_id = _row_id(self.appointments_table)
        if appointment_id is None:
            QMessageBox.information(self, "Chọn lịch", "Hãy chọn lịch hẹn cần cập nhật.")
            return
        try:
            appointment = next(
                item
                for item in self.database.list_service_appointments()
                if item["id"] == appointment_id
            )
        except (sqlite3.Error, ValueError, PermissionError, StopIteration) as error:
            QMessageBox.warning(self, "Không tìm thấy", str(error))
            return
        allowed = {
            "SCHEDULED": ("CHECKED_IN", "CANCELLED", "NO_SHOW"),
            "CHECKED_IN": ("IN_PROGRESS", "CANCELLED", "NO_SHOW"),
            "IN_PROGRESS": ("COMPLETED", "CANCELLED"),
        }.get(appointment["status"], ())
        if not allowed:
            QMessageBox.information(self, "Lịch đã kết thúc", "Lịch hẹn không còn trạng thái để chuyển.")
            return
        labels = [STATUS_LABELS[item] for item in allowed]
        selected, accepted = QInputDialog.getItem(
            self, "Cập nhật lịch", "Trạng thái", labels, 0, False
        )
        if not accepted:
            return
        status = allowed[labels.index(selected)]
        try:
            self.database.update_service_appointment_status(appointment_id, status)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể cập nhật lịch", str(error))
            return
        self.refresh()

    def reschedule(self) -> None:
        appointment_id = _row_id(self.appointments_table)
        if appointment_id is None:
            QMessageBox.information(self, "Chọn lịch", "Hãy chọn lịch hẹn cần dời.")
            return
        try:
            appointment = next(
                (
                    row
                    for row in self.database.list_service_appointments()
                    if row["id"] == appointment_id
                ),
                None,
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tải lịch hẹn", str(error))
            return
        if appointment is None:
            QMessageBox.warning(self, "Không tìm thấy", "Lịch hẹn không còn tồn tại.")
            return
        if appointment["status"] != "SCHEDULED":
            QMessageBox.information(
                self, "Không thể dời lịch", "Chỉ dời được lịch đang ở trạng thái đã đặt."
            )
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Dời lịch hẹn")
        layout = QVBoxLayout(dialog)
        scheduled = QDateTimeEdit(
            QDateTime.fromString(appointment["scheduled_at"], Qt.DateFormat.ISODate)
        )
        scheduled.setCalendarPopup(True)
        scheduled.setDisplayFormat("dd/MM/yyyy HH:mm")
        layout.addWidget(scheduled)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new_schedule = scheduled.dateTime().toString(Qt.DateFormat.ISODate)
        try:
            self.database.reschedule_service_appointment(
                appointment_id, new_schedule
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể dời lịch", str(error))
            return
        self.refresh()
