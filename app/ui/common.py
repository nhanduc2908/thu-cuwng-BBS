import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from app.database import Database


STATUS_LABELS = {
    "PENDING_INSPECTION": "Chờ kiểm tra",
    "AVAILABLE": "Đang bán",
    "RESERVED": "Đã đặt trước",
    "SOLD": "Đã bán",
    "QUARANTINE": "Cách ly",
    "TREATMENT": "Đang điều trị",
    "TRANSFERRED": "Đã chuyển đi",
    "DECEASED": "Đã mất",
}
HEALTH_STATUSES = ("Bình thường", "Theo dõi", "Đang điều trị", "Nguy kịch")


def notify_error(parent: QWidget, error: Exception) -> None:
    if isinstance(error, sqlite3.IntegrityError):
        message = (
            "Mã động vật đã tồn tại."
            if "animals.animal_code" in str(error)
            else "Không thể xóa động vật vì vẫn còn hồ sơ sức khỏe hoặc công việc chăm sóc liên quan."
        )
    else:
        message = str(error)
    QMessageBox.warning(parent, "Không thể thực hiện", message)


def make_table(headers: list[str]) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setAlternatingRowColors(True)
    return table


def set_cell(table: QTableWidget, row: int, column: int, value: Any) -> None:
    item = QTableWidgetItem("" if value is None else str(value))
    if column == 0:
        item.setData(Qt.ItemDataRole.UserRole, row)
    table.setItem(row, column, item)
