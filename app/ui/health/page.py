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
from app.ui.health.dialogs import (
    DiseaseCatalogDialog,
    HealthRecordDialog,
    VaccinationRecordDialog,
)


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

        disease_button = QPushButton("+ Bệnh / chẩn đoán", objectName="secondaryButton")
        disease_button.clicked.connect(self.add_disease_record)
        header.addWidget(disease_button)

        vaccine_button = QPushButton("+ Lịch tiêm", objectName="secondaryButton")
        vaccine_button.clicked.connect(self.add_vaccination_record)
        header.addWidget(vaccine_button)
        layout.addLayout(header)
        self.table = make_table(
            ["Ngày khám", "Mã", "Động vật", "Tình trạng", "Chẩn đoán", "Điều trị", "Bác sĩ"]
        )
        layout.addWidget(self.table)

        layout.addWidget(QLabel("Danh mục bệnh phổ biến", objectName="sectionTitle"))
        self.disease_table = make_table(["Loài", "Tên bệnh", "Mức độ", "Triệu chứng"])
        layout.addWidget(self.disease_table)

        layout.addWidget(QLabel("Lịch tiêm chủng đề xuất", objectName="sectionTitle"))
        self.vaccine_table = make_table(["Loài", "Vaccine", "Giai đoạn", "Nhắc lại sau"])
        layout.addWidget(self.vaccine_table)
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

        diseases = self.database.list_disease_catalog()
        self.disease_table.setRowCount(len(diseases))
        for row_number, disease in enumerate(diseases):
            for column, value in enumerate(
                (
                    disease["species"],
                    disease["disease_name"],
                    disease["severity"],
                    disease["symptoms"],
                )
            ):
                set_cell(self.disease_table, row_number, column, value)

        schedules = self.database.list_vaccination_schedules()
        self.vaccine_table.setRowCount(len(schedules))
        for row_number, schedule in enumerate(schedules):
            for column, value in enumerate(
                (
                    schedule["species"],
                    schedule["vaccine_name"],
                    schedule["schedule_stage"],
                    f"{schedule['recommended_months']} ({schedule['booster_interval_months']} tháng)",
                )
            ):
                set_cell(self.vaccine_table, row_number, column, value)

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

    def add_disease_record(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hãy thêm hồ sơ động vật trước khi ghi chép bệnh/chẩn đoán."
            )
            return
        dialog = DiseaseCatalogDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            values = dialog.values()
            animal = self.database.get_animal(values["animal_id"])
            self.database.add_disease_catalog_entry({
                **values,
                "species": animal["species"] if animal else "DOG",
            })
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()

    def add_vaccination_record(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hãy thêm hồ sơ động vật trước khi ghi nhận lịch tiêm."
            )
            return
        dialog = VaccinationRecordDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.add_vaccination_record(dialog.values())
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()
