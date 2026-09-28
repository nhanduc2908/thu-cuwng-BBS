import sqlite3
from typing import Any

from PySide6.QtCore import Qt
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
from app.ui.care.dialogs import CareChecklistDialog, CareTaskDialog
from app.ui.common import make_table, notify_error, set_cell


class CarePage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        header = QHBoxLayout()
        header.addWidget(QLabel("Chăm sóc", objectName="pageTitle"))
        header.addStretch()
        add_button = QPushButton("+ Tạo công việc", objectName="primaryButton")
        add_button.clicked.connect(self.add_task)
        self.add_button = add_button
        header.addWidget(add_button)
        checklist_button = QPushButton("Checklist 25 mục")
        checklist_button.clicked.connect(self.open_checklist)
        self.checklist_button = checklist_button
        header.addWidget(checklist_button)
        layout.addLayout(header)
        self.table = make_table(
            ["Ngày giờ", "Mã", "Động vật", "Công việc", "Phụ trách", "Trạng thái"]
        )
        layout.addWidget(self.table)
        complete_button = QPushButton("Đánh dấu hoàn thành")
        complete_button.clicked.connect(self.complete_task)
        self.complete_button = complete_button
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(complete_button)
        layout.addLayout(buttons)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.add_button.setVisible(enabled)
        self.checklist_button.setVisible(enabled)
        self.complete_button.setVisible(enabled)

    def refresh(self) -> None:
        tasks = self.database.list_care_tasks()
        self.table.setRowCount(len(tasks))
        for row_number, task in enumerate(tasks):
            for column, value in enumerate(
                (
                    task["scheduled_at"].replace("T", " "),
                    task["animal_code"],
                    task["animal_name"],
                    task["title"],
                    task["assigned_to"],
                    "Hoàn thành" if task["is_completed"] else "Chưa xong",
                )
            ):
                set_cell(self.table, row_number, column, value)
            self.table.item(row_number, 0).setData(
                Qt.ItemDataRole.UserRole, task["id"]
            )
            self.table.item(row_number, 0).setData(
                Qt.ItemDataRole.UserRole + 1, task["is_completed"]
            )

    def add_task(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self, "Chưa có động vật", "Hãy thêm hồ sơ động vật trước khi tạo công việc."
            )
            return
        dialog = CareTaskDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.add_care_task(dialog.values())
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()

    def open_checklist(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self,
                "Chưa có động vật",
                "Hãy thêm hồ sơ động vật trước khi đánh giá checklist.",
            )
            return
        dialog = CareChecklistDialog(self, self.database, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        try:
            self.database.save_care_checklist(
                values["animal_id"],
                values["checklist_date"],
                values["checked_by"],
                values["items"],
            )
        except (sqlite3.Error, ValueError) as error:
            notify_error(self, error)
            return
        QMessageBox.information(
            self,
            "Đã lưu",
            f"Đã lưu checklist 25 mục cho ngày {values['checklist_date']}.",
        )

    def complete_task(self) -> None:
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            QMessageBox.information(self, "Chọn công việc", "Chọn một công việc trong danh sách.")
            return
        item = self.table.item(row, 0)
        if item.data(Qt.ItemDataRole.UserRole + 1):
            QMessageBox.information(self, "Đã hoàn thành", "Công việc này đã hoàn thành.")
            return
        try:
            self.database.set_care_task_completed(
                item.data(Qt.ItemDataRole.UserRole), True
            )
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()
