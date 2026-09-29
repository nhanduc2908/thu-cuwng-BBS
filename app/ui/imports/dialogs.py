import sqlite3
from typing import Any

from PySide6.QtCore import QByteArray, QBuffer, QDate, QFileInfo, QIODevice, Qt
from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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
    MAX_PHOTO_BYTES = 8 * 1024 * 1024
    MAX_SOURCE_BYTES = 20 * 1024 * 1024

    def __init__(self, parent: QWidget, received_by: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Tiếp nhận bé vào cửa hàng")
        self.setMinimumSize(560, 700)
        self.photo_data: bytes | None = None
        self.received_by = received_by.strip()
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Chụp ảnh bé tại thời điểm bàn giao và xác nhận hiện diện tại cửa hàng. "
                "Hồ sơ sẽ được ghi nhận ngay; kiểm tra sức khỏe thực hiện riêng."
            )
        )
        self.photo_preview = QLabel("Chưa có ảnh tiếp nhận")
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setMinimumHeight(180)
        self.photo_preview.setStyleSheet(
            "background: #f4f0e6; border: 1px dashed #b8c7bd; border-radius: 10px;"
        )
        layout.addWidget(self.photo_preview)
        photo_row = QVBoxLayout()
        self.photo_button = QPushButton("Chọn ảnh vừa chụp…")
        self.photo_button.clicked.connect(self.choose_photo)
        photo_row.addWidget(self.photo_button)
        layout.addLayout(photo_row)
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
        self.received_by_label = QLabel(self.received_by or "Chưa xác định")
        form.addRow("Nhân viên tiếp nhận", self.received_by_label)
        self.confirmation = QCheckBox(
            "Tôi xác nhận bé đã được bàn giao và đang có mặt tại cửa hàng."
        )
        layout.addWidget(self.confirmation)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn ảnh tiếp nhận",
            "",
            "Ảnh (*.jpg *.jpeg *.png *.webp)",
        )
        if not path:
            return
        if QFileInfo(path).size() > self.MAX_SOURCE_BYTES:
            QMessageBox.warning(
                self, "Ảnh quá lớn", "Ảnh gốc không được vượt quá 20 MB."
            )
            return
        reader = QImageReader(path)
        reader.setAutoTransform(True)
        size = reader.size()
        if size.isValid() and size.width() * size.height() > 40_000_000:
            QMessageBox.warning(
                self, "Ảnh có độ phân giải quá lớn", "Ảnh không được vượt quá 40 megapixel."
            )
            return
        image = reader.read()
        if image.isNull():
            QMessageBox.warning(
                self, "Ảnh không hợp lệ", reader.errorString() or "Không thể đọc ảnh."
            )
            return
        image = image.scaled(
            1600,
            1600,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        encoded = QByteArray()
        buffer = QBuffer(encoded)
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            raise OSError("Không thể chuẩn bị vùng nhớ để xử lý ảnh.")
        try:
            if not image.save(buffer, "JPEG", 85):
                raise ValueError("Không thể mã hóa ảnh tiếp nhận.")
        finally:
            buffer.close()
        photo_data = bytes(encoded)
        if len(photo_data) > self.MAX_PHOTO_BYTES:
            QMessageBox.warning(
                self, "Ảnh quá lớn", "Ảnh sau xử lý vượt quá giới hạn 8 MB."
            )
            return
        self.photo_data = photo_data
        pixmap = QPixmap()
        if not pixmap.loadFromData(photo_data):
            raise ValueError("Ảnh vừa chọn không thể hiển thị.")
        self.photo_preview.setPixmap(
            pixmap.scaled(
                420,
                220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.photo_button.setText("Đổi ảnh tiếp nhận…")

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
        if self.photo_data is None:
            QMessageBox.warning(
                self, "Thiếu ảnh tiếp nhận", "Hãy chọn ảnh chụp bé tại thời điểm bàn giao."
            )
            return
        if not self.confirmation.isChecked():
            QMessageBox.warning(
                self, "Chưa xác nhận", "Hãy xác nhận bé đã có mặt tại cửa hàng."
            )
            return
        if not self.received_by:
            QMessageBox.warning(
                self,
                "Thiếu nhân viên",
                "Không xác định được nhân viên đang đăng nhập để ghi nhận tiếp nhận.",
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
            "photo_data": self.photo_data,
            "photo_mime": "image/jpeg",
            "received_by": self.received_by,
            "confirmation": self.confirmation.text(),
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
