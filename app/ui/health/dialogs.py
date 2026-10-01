import sqlite3
from typing import Any

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import HEALTH_STATUSES


class HealthRecordDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thêm hồ sơ sức khỏe")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']}", animal["id"]
            )
        self.examination_date = QDateEdit(QDate.currentDate())
        self.examination_date.setCalendarPopup(True)
        self.examination_date.setDisplayFormat("dd/MM/yyyy")
        self.health_status = QComboBox()
        self.health_status.addItems(HEALTH_STATUSES)
        self.diagnosis = QLineEdit()
        self.treatment = QLineEdit()
        self.veterinarian = QLineEdit()
        self.note = QLineEdit()
        for label, widget in (
            ("Động vật", self.animal),
            ("Ngày khám", self.examination_date),
            ("Tình trạng", self.health_status),
            ("Chẩn đoán", self.diagnosis),
            ("Điều trị", self.treatment),
            ("Bác sĩ thú y", self.veterinarian),
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
            "examination_date": self.examination_date.date().toString("yyyy-MM-dd"),
            "health_status": self.health_status.currentText(),
            "diagnosis": self.diagnosis.text().strip(),
            "treatment": self.treatment.text().strip(),
            "veterinarian": self.veterinarian.text().strip(),
            "note": self.note.text().strip(),
        }


class DiseaseCatalogDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thêm bệnh/chẩn đoán")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(f"{animal['animal_code']} — {animal['name']}", animal["id"])
        self.disease_name = QLineEdit()
        self.category = QLineEdit("GENERAL")
        self.severity = QComboBox()
        self.severity.addItems(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.symptoms = QLineEdit()
        self.treatment = QLineEdit()
        self.prevention = QLineEdit()
        for label, widget in (
            ("Động vật", self.animal),
            ("Tên bệnh", self.disease_name),
            ("Phân loại", self.category),
            ("Mức độ", self.severity),
            ("Triệu chứng", self.symptoms),
            ("Điều trị", self.treatment),
            ("Phòng ngừa", self.prevention),
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
        animal_id = self.animal.currentData()
        return {
            "animal_id": animal_id,
            "disease_code": f"USER_{animal_id}_{self.disease_name.text().strip()[:12]}".replace(" ", "_").upper(),
            "disease_name": self.disease_name.text().strip(),
            "category": self.category.text().strip() or "GENERAL",
            "severity": self.severity.currentText(),
            "description": self.symptoms.text().strip(),
            "symptoms": self.symptoms.text().strip(),
            "treatment": self.treatment.text().strip(),
            "prevention": self.prevention.text().strip(),
        }


class VaccinationRecordDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ghi nhận lịch tiêm")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(f"{animal['animal_code']} — {animal['name']}", animal["id"])
        self.vaccine_name = QLineEdit()
        self.administered_at = QDateEdit(QDate.currentDate())
        self.administered_at.setCalendarPopup(True)
        self.administered_at.setDisplayFormat("dd/MM/yyyy")
        self.next_due_at = QDateEdit(QDate.currentDate())
        self.next_due_at.setCalendarPopup(True)
        self.next_due_at.setDisplayFormat("dd/MM/yyyy")
        self.dose_number = QLineEdit("1")
        self.veterinarian = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(["COMPLETED", "SCHEDULED", "OVERDUE", "CANCELLED"])
        self.note = QLineEdit()
        for label, widget in (
            ("Động vật", self.animal),
            ("Tên vaccine", self.vaccine_name),
            ("Ngày tiêm", self.administered_at),
            ("Ngày nhắc lại", self.next_due_at),
            ("Liều số", self.dose_number),
            ("Bác sĩ thú y", self.veterinarian),
            ("Trạng thái", self.status),
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
            "vaccine_name": self.vaccine_name.text().strip(),
            "administered_at": self.administered_at.date().toString("yyyy-MM-dd"),
            "next_due_at": self.next_due_at.date().toString("yyyy-MM-dd"),
            "dose_number": int(self.dose_number.text().strip() or 1),
            "veterinarian": self.veterinarian.text().strip(),
            "status": self.status.currentText(),
            "note": self.note.text().strip(),
        }
