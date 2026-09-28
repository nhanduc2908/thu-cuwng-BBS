import sqlite3
from typing import Any

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
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

from app.modules.imports.constants import (
    INSPECTION_RESULT_LABELS,
    INSPECTION_RESULTS,
)
from app.ui.common import make_table, set_cell


class SupplierDialog(QDialog):
    def __init__(self, parent: QWidget, supplier: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            "Cập nhật nhà cung cấp" if supplier else "Thêm nhà cung cấp"
        )
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: SUP-001")
        self.name = QLineEdit()
        self.contact_person = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QLineEdit()
        self.tax_code = QLineEdit()
        self.note = QTextEdit()
        self.note.setMaximumHeight(80)
        for label, widget in (
            ("Mã nhà cung cấp *", self.code),
            ("Tên nhà cung cấp *", self.name),
            ("Người liên hệ", self.contact_person),
            ("Điện thoại", self.phone),
            ("Email", self.email),
            ("Địa chỉ", self.address),
            ("Mã số thuế", self.tax_code),
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
        if supplier:
            self.code.setText(supplier["supplier_code"])
            self.name.setText(supplier["name"])
            self.contact_person.setText(supplier["contact_person"])
            self.phone.setText(supplier["phone"])
            self.email.setText(supplier["email"])
            self.address.setText(supplier["address"])
            self.tax_code.setText(supplier["tax_code"])
            self.note.setPlainText(supplier["note"])

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Mã và tên nhà cung cấp là bắt buộc.",
            )
            return
        self.accept()

    def values(self) -> dict[str, str]:
        return {
            "supplier_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "contact_person": self.contact_person.text().strip(),
            "phone": self.phone.text().strip(),
            "email": self.email.text().strip(),
            "address": self.address.text().strip(),
            "tax_code": self.tax_code.text().strip(),
            "note": self.note.toPlainText().strip(),
        }


class ImportBatchDialog(QDialog):
    def __init__(self, parent: QWidget, suppliers: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo lô nhập động vật")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: IMP-2026-001")
        self.supplier = QComboBox()
        for supplier in suppliers:
            self.supplier.addItem(
                f"{supplier['supplier_code']} — {supplier['name']}",
                supplier["id"],
            )
        self.import_date = QDateEdit(QDate.currentDate())
        self.import_date.setCalendarPopup(True)
        self.import_date.setDisplayFormat("dd/MM/yyyy")
        self.note = QLineEdit()
        for label, widget in (
            ("Mã lô nhập *", self.code),
            ("Nhà cung cấp", self.supplier),
            ("Ngày nhập", self.import_date),
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

    def _validate(self) -> None:
        if not self.code.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã lô nhập là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "batch_code": self.code.text().strip(),
            "supplier_id": self.supplier.currentData(),
            "import_date": self.import_date.date().toString("yyyy-MM-dd"),
            "note": self.note.text().strip(),
        }


class ImportAnimalDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ghi nhận động vật trong lô nhập")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Sau khi lưu, động vật sẽ ở trạng thái “Chờ kiểm tra”.")
        )
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: PET-2026-001")
        self.name = QLineEdit()
        self.species = QLineEdit()
        self.breed = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(("Chưa rõ", "Đực", "Cái"))
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1_000_000_000)
        self.purchase_price.setDecimals(0)
        self.purchase_price.setSuffix(" ₫")
        self.sale_price = QDoubleSpinBox()
        self.sale_price.setRange(0, 1_000_000_000)
        self.sale_price.setDecimals(0)
        self.sale_price.setSuffix(" ₫")
        self.origin = QLineEdit()
        for label, widget in (
            ("Mã động vật *", self.code),
            ("Tên *", self.name),
            ("Loài *", self.species),
            ("Giống", self.breed),
            ("Giới tính", self.gender),
            ("Ngày sinh", self.birth_date),
            ("Giá nhập", self.purchase_price),
            ("Giá bán dự kiến", self.sale_price),
            ("Nguồn gốc", self.origin),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if (
            not self.code.text().strip()
            or not self.name.text().strip()
            or not self.species.text().strip()
        ):
            QMessageBox.warning(
                self, "Thiếu thông tin", "Mã, tên và loài động vật là bắt buộc."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "animal_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "species": self.species.text().strip(),
            "breed": self.breed.text().strip(),
            "gender": self.gender.currentText(),
            "birth_date": self.birth_date.date().toString("yyyy-MM-dd"),
            "purchase_price": self.purchase_price.value(),
            "sale_price": self.sale_price.value(),
            "origin": self.origin.text().strip(),
        }


class InspectionDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kiểm tra động vật đầu vào")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']} ({animal['species']})",
                animal["id"],
            )
        self.result = QComboBox()
        for result in INSPECTION_RESULTS:
            self.result.addItem(INSPECTION_RESULT_LABELS[result], result)
        self.symptoms = QLineEdit()
        self.checked_by = QLineEdit()
        self.note = QTextEdit()
        self.note.setMaximumHeight(90)
        for label, widget in (
            ("Động vật", self.animal),
            ("Kết quả", self.result),
            ("Triệu chứng/dấu hiệu", self.symptoms),
            ("Người kiểm tra", self.checked_by),
            ("Ghi chú", self.note),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "animal_id": self.animal.currentData(),
            "inspected_at": QDate.currentDate().toString("yyyy-MM-dd"),
            "result": self.result.currentData(),
            "symptoms": self.symptoms.text().strip(),
            "checked_by": self.checked_by.text().strip(),
            "note": self.note.toPlainText().strip(),
        }


class InspectionHistoryDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        database: Any,
        batch_id: int,
        animal_id: int,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Lịch sử kiểm tra đầu vào")
        self.resize(780, 400)
        layout = QVBoxLayout(self)
        self.table = make_table(
            ["Ngày", "Động vật", "Kết quả", "Dấu hiệu", "Người kiểm tra", "Ghi chú"]
        )
        records = database.list_inspections(batch_id, animal_id)
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            for column, value in enumerate(
                (
                    record["inspected_at"],
                    f"{record['animal_code']} — {record['animal_name']}",
                    INSPECTION_RESULT_LABELS[record["result"]],
                    record["symptoms"],
                    record["checked_by"],
                    record["note"],
                )
            ):
                set_cell(self.table, row, column, value)
        layout.addWidget(self.table)
