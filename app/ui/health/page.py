import sqlite3

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table, notify_error, set_cell
from app.ui.health.dialogs import HealthRecordDialog


class HealthPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        header = QHBoxLayout()
        header.addWidget(QLabel("Hồ sơ sức khỏe", objectName="pageTitle"))
        header.addStretch()
        add_button = QPushButton("+ Ghi nhận khám", objectName="primaryButton")
        add_button.clicked.connect(self.add_record)
        self.add_button = add_button
        header.addWidget(add_button)
        layout.addLayout(header)
        self.table = make_table(
            ["Ngày khám", "Mã", "Động vật", "Tình trạng", "Chẩn đoán", "Điều trị", "Bác sĩ"]
        )
        layout.addWidget(self.table)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.add_button.setVisible(enabled)

    def refresh(self) -> None:
        records = self.database.list_health_records()
        self.table.setRowCount(len(records))
        for row_number, record in enumerate(records):
            for column, value in enumerate(
                (
                    record["examination_date"],
                    record["animal_code"],
                    record["animal_name"],
                    record["health_status"],
                    record["diagnosis"],
                    record["treatment"],
                    record["veterinarian"],
                )
            ):
                set_cell(self.table, row_number, column, value)

    def add_record(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hãy thêm hồ sơ động vật trước khi ghi nhận sức khỏe."
            )
            return
        dialog = HealthRecordDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.add_health_record(dialog.values())
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()
