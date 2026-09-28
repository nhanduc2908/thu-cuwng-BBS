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
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.animals.constants import ANIMAL_STATUSES
from app.ui.common import HEALTH_STATUSES, STATUS_LABELS


class AnimalDialog(QDialog):
    def __init__(self, parent: QWidget, animal: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật động vật" if animal else "Thêm động vật")
        self.setMinimumSize(560, 680)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Hồ sơ gồm 25 đặc điểm cá thể, sức khỏe và nhu cầu chăm sóc.")
        )
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        form_container = QWidget()
        form = QFormLayout()
        form_container.setLayout(form)
        scroll_area.setWidget(form_container)
        layout.addWidget(scroll_area, 1)

        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: PET-0001")
        self.name = QLineEdit()
        self.species = QLineEdit()
        self.species.setPlaceholderText("Chó, mèo, chim...")
        self.breed = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(("Chưa rõ", "Đực", "Cái"))
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setSpecialValueText("Chưa nhập")
        self.birth_date.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
        self.birth_date.setDate(QDate(1900, 1, 1))
        self.intake_date = self._make_date_edit()
        self.last_vet_visit = self._make_date_edit()
        self.color = QLineEdit()
        self.weight = QDoubleSpinBox()
        self.weight.setRange(0, 100000)
        self.weight.setDecimals(2)
        self.weight.setSuffix(" kg")
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1_000_000_000)
        self.purchase_price.setDecimals(0)
        self.purchase_price.setSuffix(" ₫")
        self.sale_price = QDoubleSpinBox()
        self.sale_price.setRange(0, 1_000_000_000)
        self.sale_price.setDecimals(0)
        self.sale_price.setSuffix(" ₫")
        self.status = QComboBox()
        for status in ANIMAL_STATUSES:
            self.status.addItem(STATUS_LABELS[status], status)
        self.health_status = QComboBox()
        self.health_status.addItems(HEALTH_STATUSES)
        self.origin = QLineEdit()
        self.supplier_name = QLineEdit()
        self.microchip_id = QLineEdit()
        self.cage_location = QLineEdit()
        self.diet = QLineEdit()
        self.feeding_schedule = QLineEdit()
        self.allergies = QLineEdit()
        self.vaccination_status = QLineEdit()
        self.exercise_needs = QLineEdit()
        self.behavior = QLineEdit()
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)

        fields = (
            ("Mã động vật *", self.code),
            ("Tên *", self.name),
            ("Loài *", self.species),
            ("Giống", self.breed),
            ("Giới tính", self.gender),
            ("Ngày sinh", self.birth_date),
            ("Màu sắc", self.color),
            ("Cân nặng", self.weight),
            ("Giá nhập", self.purchase_price),
            ("Giá bán", self.sale_price),
            ("Trạng thái", self.status),
            ("Sức khỏe", self.health_status),
            ("Nguồn gốc", self.origin),
            ("Nhà cung cấp", self.supplier_name),
            ("Ngày nhập", self.intake_date),
            ("Mã microchip", self.microchip_id),
            ("Chuồng/khu vực ở", self.cage_location),
            ("Chế độ ăn", self.diet),
            ("Lịch và khẩu phần ăn", self.feeding_schedule),
            ("Dị ứng/nhạy cảm", self.allergies),
            ("Tiêm phòng", self.vaccination_status),
            ("Lần khám thú y gần nhất", self.last_vet_visit),
            ("Nhu cầu vận động", self.exercise_needs),
            ("Đặc điểm hành vi", self.behavior),
            ("Mô tả", self.description),
        )
        if len(fields) != 25:
            raise RuntimeError("Hồ sơ động vật phải có đúng 25 đặc điểm.")
        for index, (label, widget) in enumerate(fields, start=1):
            form.addRow(f"{index:02d}. {label}", widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if animal:
            self._load_animal(animal)

    @staticmethod
    def _make_date_edit() -> QDateEdit:
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setSpecialValueText("Chưa nhập")
        date_edit.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
        date_edit.setDate(QDate(1900, 1, 1))
        return date_edit

    @staticmethod
    def _date_value(date_edit: QDateEdit) -> str:
        if date_edit.date() == QDate(1900, 1, 1):
            return ""
        return date_edit.date().toString("yyyy-MM-dd")

    def _load_animal(self, animal: sqlite3.Row) -> None:
        self.code.setText(animal["animal_code"])
        self.name.setText(animal["name"])
        self.species.setText(animal["species"])
        self.breed.setText(animal["breed"])
        self.gender.setCurrentText(animal["gender"])
        if animal["birth_date"]:
            self.birth_date.setDate(QDate.fromString(animal["birth_date"], "yyyy-MM-dd"))
        self.color.setText(animal["color"])
        self.weight.setValue(animal["weight"] or 0)
        self.purchase_price.setValue(animal["purchase_price"])
        self.sale_price.setValue(animal["sale_price"])
        self.status.setCurrentIndex(self.status.findData(animal["status"]))
        self.health_status.setCurrentText(animal["health_status"])
        self.origin.setText(animal["origin"])
        self.description.setPlainText(animal["description"])
        self.supplier_name.setText(animal["supplier_name"])
        if animal["intake_date"]:
            self.intake_date.setDate(QDate.fromString(animal["intake_date"], "yyyy-MM-dd"))
        self.microchip_id.setText(animal["microchip_id"])
        self.cage_location.setText(animal["cage_location"])
        self.diet.setText(animal["diet"])
        self.feeding_schedule.setText(animal["feeding_schedule"])
        self.allergies.setText(animal["allergies"])
        self.vaccination_status.setText(animal["vaccination_status"])
        if animal["last_vet_visit"]:
            self.last_vet_visit.setDate(
                QDate.fromString(animal["last_vet_visit"], "yyyy-MM-dd")
            )
        self.exercise_needs.setText(animal["exercise_needs"])
        self.behavior.setText(animal["behavior"])

    def _validate_and_accept(self) -> None:
        if (
            not self.code.text().strip()
            or not self.name.text().strip()
            or not self.species.text().strip()
        ):
            QMessageBox.warning(self, "Thiếu thông tin", "Mã, tên và loài là các trường bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "animal_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "species": self.species.text().strip(),
            "breed": self.breed.text().strip(),
            "gender": self.gender.currentText(),
            "birth_date": self._date_value(self.birth_date),
            "color": self.color.text().strip(),
            "weight": self.weight.value() or None,
            "origin": self.origin.text().strip(),
            "purchase_price": self.purchase_price.value(),
            "sale_price": self.sale_price.value(),
            "status": self.status.currentData(),
            "health_status": self.health_status.currentText(),
            "description": self.description.toPlainText().strip(),
            "supplier_name": self.supplier_name.text().strip(),
            "intake_date": self._date_value(self.intake_date),
            "microchip_id": self.microchip_id.text().strip(),
            "cage_location": self.cage_location.text().strip(),
            "diet": self.diet.text().strip(),
            "feeding_schedule": self.feeding_schedule.text().strip(),
            "allergies": self.allergies.text().strip(),
            "vaccination_status": self.vaccination_status.text().strip(),
            "last_vet_visit": self._date_value(self.last_vet_visit),
            "exercise_needs": self.exercise_needs.text().strip(),
            "behavior": self.behavior.text().strip(),
        }
