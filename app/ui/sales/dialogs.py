import sqlite3
from typing import Any

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
)

from app.modules.sales.constants import PAYMENT_METHODS, PAYMENT_METHOD_LABELS


class CustomerDialog(QDialog):
    def __init__(self, parent: QWidget, customer: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật khách hàng" if customer else "Thêm khách hàng")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: CUS-001")
        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QLineEdit()
        self.note = QTextEdit()
        self.note.setMaximumHeight(75)
        for label, widget in (
            ("Mã khách hàng *", self.code),
            ("Họ tên *", self.name),
            ("Điện thoại", self.phone),
            ("Email", self.email),
            ("Địa chỉ", self.address),
            ("Ghi chú", self.note),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if customer:
            self.code.setText(customer["customer_code"])
            self.name.setText(customer["name"])
            self.phone.setText(customer["phone"])
            self.email.setText(customer["email"])
            self.address.setText(customer["address"])
            self.note.setPlainText(customer["note"])

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Mã khách hàng và họ tên là bắt buộc."
            )
            return
        self.accept()

    def values(self) -> dict[str, str]:
        return {
            "customer_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "phone": self.phone.text().strip(),
            "email": self.email.text().strip(),
            "address": self.address.text().strip(),
            "note": self.note.toPlainText().strip(),
        }


class ReservationDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        customers: list[sqlite3.Row],
        animals: list[sqlite3.Row],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Giữ chỗ động vật")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.customer = QComboBox()
        for customer in customers:
            self.customer.addItem(
                f"{customer['customer_code']} — {customer['name']}",
                customer["id"],
            )
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']} ({animal['species']}) · "
                f"{animal['sale_price']:,.0f} ₫",
                animal["id"],
            )
        self.expires_at = QDateEdit(QDate.currentDate().addDays(3))
        self.expires_at.setCalendarPopup(True)
        self.expires_at.setDisplayFormat("dd/MM/yyyy")
        self.deposit = QDoubleSpinBox()
        self.deposit.setRange(0, 1_000_000_000)
        self.deposit.setDecimals(0)
        self.deposit.setSuffix(" ₫")
        self.deposit_method = QComboBox()
        for key in PAYMENT_METHODS:
            self.deposit_method.addItem(PAYMENT_METHOD_LABELS[key], key)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        for label, widget in (
            ("Khách hàng", self.customer),
            ("Động vật", self.animal),
            ("Hạn giữ chỗ", self.expires_at),
            ("Tiền cọc", self.deposit),
            ("Hình thức nhận cọc", self.deposit_method),
            ("Mã giao dịch", self.reference),
            ("Ghi chú", self.note),
        ):
            form.addRow(label, widget)
        layout.addWidget(
            QLabel("Nếu đã nhận cọc, cần ghi nhận hoàn cọc trước khi giải phóng chỗ.")
        )
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if self.expires_at.date() < QDate.currentDate():
            QMessageBox.warning(
                self, "Ngày không hợp lệ", "Hạn giữ chỗ không thể ở trước hôm nay."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer.currentData(),
            "animal_id": self.animal.currentData(),
            "reserved_at": QDate.currentDate().toString("yyyy-MM-dd"),
            "expires_at": self.expires_at.date().toString("yyyy-MM-dd"),
            "deposit": self.deposit.value(),
            "deposit_method": self.deposit_method.currentData(),
            "deposit_reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }


class SalesOrderDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        customers: list[sqlite3.Row],
        animals: list[sqlite3.Row],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo đơn bán hàng")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: SO-2026-001")
        self.customer = QComboBox()
        for customer in customers:
            self.customer.addItem(
                f"{customer['customer_code']} — {customer['name']}",
                customer["id"],
            )
        self.animal_list = QListWidget()
        self.animal_list.setMinimumHeight(150)
        self.animals = animals
        self.customer.currentIndexChanged.connect(self._refresh_animals)
        self.ordered_at = QDateEdit(QDate.currentDate())
        self.ordered_at.setCalendarPopup(True)
        self.ordered_at.setDisplayFormat("dd/MM/yyyy")
        self.note = QLineEdit()
        form.addRow("Mã đơn *", self.code)
        form.addRow("Khách hàng", self.customer)
        form.addRow("Ngày bán", self.ordered_at)
        form.addRow("Ghi chú", self.note)
        layout.addLayout(form)
        layout.addWidget(QLabel("Chọn một hoặc nhiều động vật"))
        layout.addWidget(self.animal_list)
        layout.addWidget(
            QLabel("Đơn bắt đầu ở trạng thái chưa thanh toán; động vật được giữ trong đơn.")
        )
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._refresh_animals()

    def _refresh_animals(self, *_: Any) -> None:
        self.animal_list.clear()
        customer_id = self.customer.currentData()
        for animal in self.animals:
            if animal["status"] == "AVAILABLE" or (
                animal["status"] == "RESERVED"
                and animal["reservation_customer_id"] == customer_id
            ):
                item = QListWidgetItem(
                    f"{animal['animal_code']} — {animal['name']} ({animal['species']}) · "
                    f"{animal['sale_price']:,.0f} ₫"
                )
                item.setData(Qt.ItemDataRole.UserRole, animal["id"])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.animal_list.addItem(item)

    def _validate(self) -> None:
        if not self.code.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã đơn hàng là bắt buộc.")
            return
        if not any(
            self.animal_list.item(index).checkState() == Qt.CheckState.Checked
            for index in range(self.animal_list.count())
        ):
            QMessageBox.warning(
                self,
                "Chưa chọn động vật",
                "Hãy chọn ít nhất một động vật đủ điều kiện bán.",
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "order_code": self.code.text().strip(),
            "customer_id": self.customer.currentData(),
            "animal_ids": [
                self.animal_list.item(index).data(Qt.ItemDataRole.UserRole)
                for index in range(self.animal_list.count())
                if self.animal_list.item(index).checkState() == Qt.CheckState.Checked
            ],
            "ordered_at": self.ordered_at.date().toString("yyyy-MM-dd"),
            "note": self.note.text().strip(),
        }


class ProductSalesOrderDialog(QDialog):
    def __init__(
        self, parent: QWidget, database: Any, customers: list[sqlite3.Row]
    ) -> None:
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Tạo đơn bán sản phẩm & combo")
        self.resize(1100, 760)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText(
            f"Ví dụ: SO-P-{QDate.currentDate().toString('yyyyMMdd')}-001"
        )
        self.customer = QComboBox()
        for customer in customers:
            self.customer.addItem(
                f"{customer['customer_code']} — {customer['name']}",
                customer["id"],
            )
        self.customer.currentIndexChanged.connect(self._refresh_catalog)
        self.ordered_at = QDateEdit(QDate.currentDate())
        self.ordered_at.setCalendarPopup(True)
        self.ordered_at.setDisplayFormat("dd/MM/yyyy")
        self.note = QLineEdit()
        form.addRow("Mã đơn *", self.code)
        form.addRow("Khách hàng", self.customer)
        form.addRow("Ngày bán", self.ordered_at)
        form.addRow("Ghi chú", self.note)
        layout.addLayout(form)
        layout.addWidget(
            QLabel(
                "Giá demo cần cửa hàng xác minh. Giá hội viên áp dụng theo hạng đang "
                "có hiệu lực; tồn chỉ bị trừ khi đơn thanh toán đủ."
            )
        )
        self.tabs = QTabWidget()
        self.products_table = self._create_select_table(
            ["Chọn", "SKU", "Sản phẩm", "Danh mục", "Còn bán", "Giá", "Số lượng"]
        )
        self.combos_table = self._create_select_table(
            ["Chọn", "Mã combo", "Combo", "Loài", "Thành phần", "Giá", "Số lượng"]
        )
        self.tabs.addTab(self.products_table, "Sản phẩm")
        self.tabs.addTab(self.combos_table, "Combo")
        layout.addWidget(self.tabs, 1)
        self.notice = QLabel("")
        layout.addWidget(self.notice)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.product_rows: list[dict[str, Any]] = []
        self.combo_rows: list[dict[str, Any]] = []
        self._refresh_catalog()

    @staticmethod
    def _create_select_table(headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        return table

    def _fill_selection_table(
        self,
        table: QTableWidget,
        entries: list[dict[str, Any]],
        columns: tuple[str, ...],
        available: Any,
    ) -> None:
        table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            is_available = bool(available(entry))
            check = QTableWidgetItem()
            check.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            check.setCheckState(Qt.CheckState.Unchecked)
            if not is_available:
                check.setFlags(Qt.ItemFlag.ItemIsEnabled)
            check.setData(Qt.ItemDataRole.UserRole, int(entry["id"]))
            table.setItem(row, 0, check)
            for column, key in enumerate(columns, start=1):
                value = entry.get(key, "")
                if key == "sale_price":
                    value = f"{float(value):,.0f} VND"
                elif key == "available":
                    value = f"{float(value):g}"
                set_item = QTableWidgetItem(str(value or ""))
                table.setItem(row, column, set_item)
            quantity = QDoubleSpinBox()
            maximum = float(entry.get("max_quantity", entry.get("available", 0)))
            quantity.setRange(0.001, max(0.001, min(maximum, 100_000)))
            quantity.setDecimals(3)
            quantity.setValue(1)
            quantity.setEnabled(is_available)
            if maximum < 1:
                quantity.setEnabled(False)
            table.setCellWidget(row, len(columns) + 1, quantity)

    def _refresh_catalog(self, *_: Any) -> None:
        customer_id = self.customer.currentData()
        if customer_id is None:
            return
        try:
            products = self.database.list_saleable_products(int(customer_id))
            combos = self.database.list_saleable_combos(int(customer_id))
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.notice.setText(f"Không thể tải catalog bán hàng: {error}")
            return
        self.product_rows = products
        self.combo_rows = combos
        for product in products:
            product["display_name"] = product["name"]
            if product["pack_size"]:
                product["display_name"] += f" · {product['pack_size']}"
        self._fill_selection_table(
            self.products_table,
            products,
            ("item_code", "display_name", "catalog_category", "available", "sale_price"),
            lambda product: float(product["available"]) > 0,
        )
        self._fill_selection_table(
            self.combos_table,
            combos,
            (
                "combo_code",
                "name",
                "target_species",
                "component_count",
                "sale_price",
            ),
            lambda combo: bool(combo["available"]),
        )
        self.notice.setText(
            "Giá đã tính theo hội viên đang hiệu lực (nếu có). "
            "Combo cần đủ tồn từng SKU thành phần mới được chọn."
        )

    @staticmethod
    def _selected_lines(table: QTableWidget, key: str) -> list[dict[str, Any]]:
        lines: list[dict[str, Any]] = []
        for row in range(table.rowCount()):
            check = table.item(row, 0)
            if check is None or check.checkState() != Qt.CheckState.Checked:
                continue
            lines.append(
                {
                    key: int(check.data(Qt.ItemDataRole.UserRole)),
                    "quantity": table.cellWidget(row, table.columnCount() - 1).value(),
                }
            )
        return lines

    def _validate(self) -> None:
        if not self.code.text().strip():
            QMessageBox.warning(self, "Thiếu mã đơn", "Mã đơn hàng là bắt buộc.")
            return
        if not self._selected_lines(self.products_table, "item_id") and not self._selected_lines(
            self.combos_table, "combo_id"
        ):
            QMessageBox.warning(
                self, "Chưa chọn hàng", "Hãy chọn ít nhất một sản phẩm hoặc combo."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "order_code": self.code.text().strip(),
            "customer_id": int(self.customer.currentData()),
            "ordered_at": self.ordered_at.date().toString("yyyy-MM-dd"),
            "note": self.note.text().strip(),
            "product_lines": self._selected_lines(self.products_table, "item_id"),
            "combo_lines": self._selected_lines(self.combos_table, "combo_id"),
        }


class PaymentDialog(QDialog):
    def __init__(self, parent: QWidget, balance: float) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ghi nhận thanh toán")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Còn phải thu: {balance:,.0f} ₫"))
        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, max(balance, 0.01))
        self.amount.setValue(max(balance, 0.01))
        self.amount.setDecimals(2)
        self.amount.setSuffix(" ₫")
        self.method = QComboBox()
        for key in PAYMENT_METHODS:
            self.method.addItem(PAYMENT_METHOD_LABELS[key], key)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Số tiền", self.amount)
        form.addRow("Phương thức", self.method)
        form.addRow("Mã giao dịch", self.reference)
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
            "method": self.method.currentData(),
            "paid_at": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }


class RefundDepositDialog(QDialog):
    def __init__(
        self, parent: QWidget, reservation_id: int, outstanding: float
    ) -> None:
        super().__init__(parent)
        self.reservation_id = reservation_id
        self.setWindowTitle("Ghi nhận hoàn tiền cọc")
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                f"Tiền cọc chưa hoàn: {outstanding:,.0f} ₫. "
                "Chỉ ghi nhận sau khi đã thực hiện hoàn tiền."
            )
        )
        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, max(outstanding, 0.01))
        self.amount.setValue(max(outstanding, 0.01))
        self.amount.setDecimals(2)
        self.amount.setSuffix(" ₫")
        self.method = QComboBox()
        for key in PAYMENT_METHODS:
            self.method.addItem(PAYMENT_METHOD_LABELS[key], key)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Số tiền hoàn", self.amount)
        form.addRow("Hình thức", self.method)
        form.addRow("Mã giao dịch", self.reference)
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
            "method": self.method.currentData(),
            "refunded_at": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }
