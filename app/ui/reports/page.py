import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QDateEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table


REPORTS = {
    "inventory": "Tồn kho",
    "sales": "Bán hàng",
    "health": "Sức khỏe",
}

REPORT_HEADERS = {
    "inventory": {
        "item_code": "Mã vật tư",
        "name": "Tên vật tư",
        "category": "Loại",
        "unit": "Đơn vị",
        "stock_quantity": "Tổng tồn",
        "usable_quantity": "Tồn dùng được",
        "minimum_stock": "Tồn tối thiểu",
        "is_active": "Đang hoạt động",
    },
    "sales": {
        "order_code": "Mã đơn",
        "ordered_at": "Ngày bán",
        "customer_code": "Mã khách",
        "customer": "Khách hàng",
        "status": "Trạng thái",
        "total_amount": "Tổng tiền",
        "paid_amount": "Đã thanh toán",
        "item_count": "Số động vật",
    },
    "health": {
        "examination_date": "Ngày khám",
        "animal_code": "Mã động vật",
        "animal_name": "Tên động vật",
        "species": "Loài",
        "health_status": "Tình trạng",
        "diagnosis": "Chẩn đoán",
        "treatment": "Điều trị",
        "veterinarian": "Bác sĩ thú y",
        "note": "Ghi chú",
    },
}


class ReportsPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Báo cáo và phân tích", objectName="pageTitle"))
        toolbar = QHBoxLayout()
        self.report_type = QComboBox()
        for key, label in REPORTS.items():
            self.report_type.addItem(label, key)
        today = QDate.currentDate()
        self.start_date = QDateEdit(today.addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date = QDateEdit(today)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.refresh_button = QPushButton("Tạo báo cáo")
        self.refresh_button.clicked.connect(self.refresh_report)
        self.export_button = QPushButton("Xuất CSV")
        self.export_button.clicked.connect(self.export_csv)
        for widget in (
            QLabel("Loại báo cáo"),
            self.report_type,
            QLabel("Từ"),
            self.start_date,
            QLabel("Đến"),
            self.end_date,
            self.refresh_button,
            self.export_button,
        ):
            toolbar.addWidget(widget)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        self.report_type.currentIndexChanged.connect(self._report_type_changed)
        self.summary = QLabel()
        layout.addWidget(self.summary)
        self.table = make_table([])
        layout.addWidget(self.table)
        self._report_type_changed()
        self.refresh_report()

    def _report_type_changed(self, *_: object) -> None:
        is_inventory = self.report_type.currentData() == "inventory"
        self.start_date.setEnabled(not is_inventory)
        self.end_date.setEnabled(not is_inventory)

    def refresh(self, *_: object) -> None:
        self.refresh_report()

    def refresh_report(self) -> None:
        report_type = self.report_type.currentData()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        try:
            if report_type == "inventory":
                rows = self.database.report_inventory()
            elif report_type == "sales":
                rows = self.database.report_sales(start_date, end_date)
            else:
                rows = self.database.report_health(start_date, end_date)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tạo báo cáo", str(error))
            return
        headers = list(rows[0].keys()) if rows else self._empty_headers(report_type)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(
            [REPORT_HEADERS[report_type][header] for header in headers]
        )
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, header in enumerate(headers):
                value = row[header]
                self.table.setItem(
                    row_index,
                    column,
                    QTableWidgetItem("" if value is None else str(value)),
                )
        self.summary.setText(f"{REPORTS[report_type]}: {len(rows)} bản ghi")

    @staticmethod
    def _empty_headers(report_type: str) -> list[str]:
        return {
            "inventory": [
                "item_code",
                "name",
                "category",
                "unit",
                "stock_quantity",
                "usable_quantity",
                "minimum_stock",
                "is_active",
            ],
            "sales": [
                "order_code",
                "ordered_at",
                "customer_code",
                "customer",
                "status",
                "total_amount",
                "paid_amount",
                "item_count",
            ],
            "health": [
                "examination_date",
                "animal_code",
                "animal_name",
                "species",
                "health_status",
                "diagnosis",
                "treatment",
                "veterinarian",
                "note",
            ],
        }[report_type]

    def export_csv(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu báo cáo CSV",
            f"{self.report_type.currentData()}_{datetime.now():%Y%m%d}.csv",
            "CSV (*.csv)",
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        headers = [
            self.table.horizontalHeaderItem(column).text()
            for column in range(self.table.columnCount())
        ]
        try:
            with path.open("w", newline="", encoding="utf-8-sig") as output:
                writer = csv.writer(output)
                writer.writerow(headers)
                for row in range(self.table.rowCount()):
                    writer.writerow(
                        [
                            self.table.item(row, column).text()
                            if self.table.item(row, column)
                            else ""
                            for column in range(self.table.columnCount())
                        ]
                    )
        except OSError as error:
            QMessageBox.warning(self, "Không thể xuất báo cáo", str(error))
            return
        QMessageBox.information(self, "Đã xuất", f"Đã lưu báo cáo tại:\n{path}")
