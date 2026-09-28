import sqlite3
from typing import Any

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.modules.inventory.constants import INVENTORY_CATEGORIES, INVENTORY_CATEGORY_LABELS


class InventoryItemDialog(QDialog):
    def __init__(
        self, parent: QWidget, item: sqlite3.Row | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật vật tư" if item else "Thêm vật tư")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.category = QComboBox()
        for value in INVENTORY_CATEGORIES:
            self.category.addItem(INVENTORY_CATEGORY_LABELS[value], value)
        self.unit = QLineEdit()
        self.minimum = QDoubleSpinBox()
        self.minimum.setRange(0, 1_000_000_000)
        self.minimum.setDecimals(3)
        self.description = QTextEdit()
        self.description.setMaximumHeight(75)
        for label, widget in (
            ("Mã vật tư *", self.code),
            ("Tên *", self.name),
            ("Loại", self.category),
            ("Đơn vị tính *", self.unit),
            ("Ngưỡng tồn tối thiểu", self.minimum),
            ("Mô tả", self.description),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if item:
            self.code.setText(item["item_code"])
            self.name.setText(item["name"])
            self.category.setCurrentIndex(self.category.findData(item["category"]))
            self.unit.setText(item["unit"])
            self.minimum.setValue(item["minimum_stock"])
            self.description.setPlainText(item["description"])

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Mã vật tư và tên là bắt buộc."
            )
            return
        if not self.unit.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Đơn vị tính là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "item_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "category": self.category.currentData(),
            "unit": self.unit.text().strip(),
            "minimum_stock": self.minimum.value(),
            "description": self.description.toPlainText().strip(),
        }


class ReceiveStockDialog(QDialog):
    def __init__(self, parent: QWidget, unit: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nhập kho theo lô")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.batch_code = QLineEdit()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.001, 1_000_000_000)
        self.quantity.setDecimals(3)
        self.quantity.setSuffix(f" {unit}")
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setRange(0, 1_000_000_000)
        self.unit_cost.setDecimals(2)
        self.unit_cost.setSuffix(" ₫")
        self.expiry_enabled = QCheckBox("Có hạn sử dụng")
        self.expiry_date = QDateEdit(QDate.currentDate().addYears(1))
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("dd/MM/yyyy")
        self.expiry_enabled.toggled.connect(self.expiry_date.setEnabled)
        self.expiry_date.setEnabled(False)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Mã lô *", self.batch_code)
        form.addRow("Số lượng *", self.quantity)
        form.addRow("Giá nhập / đơn vị", self.unit_cost)
        form.addRow(self.expiry_enabled)
        form.addRow("Hạn sử dụng", self.expiry_date)
        form.addRow("Mã chứng từ", self.reference)
        form.addRow("Ghi chú", self.note)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if not self.batch_code.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã lô là bắt buộc.")
            return
        if (
            self.expiry_enabled.isChecked()
            and self.expiry_date.date() < QDate.currentDate()
        ):
            QMessageBox.warning(
                self, "Hạn sử dụng không hợp lệ", "Không thể nhập lô đã hết hạn."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "batch_code": self.batch_code.text().strip(),
            "quantity": self.quantity.value(),
            "unit_cost": self.unit_cost.value(),
            "expiry_date": (
                self.expiry_date.date().toString("yyyy-MM-dd")
                if self.expiry_enabled.isChecked()
                else None
            ),
            "occurred_on": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }


class ConsumeStockDialog(QDialog):
    def __init__(
        self, parent: QWidget, unit: str, animals: list[sqlite3.Row]
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Xuất kho sử dụng")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.001, 1_000_000_000)
        self.quantity.setDecimals(3)
        self.quantity.setSuffix(f" {unit}")
        self.animal = QComboBox()
        self.animal.addItem("Không gắn với cá thể", None)
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']}", animal["id"]
            )
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Số lượng *", self.quantity)
        form.addRow("Động vật (nếu có)", self.animal)
        form.addRow("Mã phiếu", self.reference)
        form.addRow("Ghi chú", self.note)
        layout.addWidget(
            QLabel("Xuất theo lô hết hạn gần nhất; không thể xuất lô đã hết hạn.")
        )
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "quantity": self.quantity.value(),
            "animal_id": self.animal.currentData(),
            "occurred_on": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }
