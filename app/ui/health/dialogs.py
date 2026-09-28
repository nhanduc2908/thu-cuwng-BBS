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
