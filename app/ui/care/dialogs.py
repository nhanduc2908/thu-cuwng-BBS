import sqlite3
from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.care.constants import CARE_CHECKLIST_ITEMS


class CareTaskDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo công việc chăm sóc")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']}", animal["id"]
            )
        self.title = QLineEdit()
        self.title.setPlaceholderText("Ví dụ: Cho ăn, vệ sinh chuồng")
        self.scheduled_date = QDateEdit(QDate.currentDate())
        self.scheduled_date.setCalendarPopup(True)
        self.scheduled_date.setDisplayFormat("dd/MM/yyyy")
        self.scheduled_time = QTimeEdit()
        self.scheduled_time.setDisplayFormat("HH:mm")
        self.assigned_to = QLineEdit()
        self.note = QLineEdit()
        for label, widget in (
            ("Động vật", self.animal),
            ("Công việc *", self.title),
            ("Ngày", self.scheduled_date),
            ("Giờ", self.scheduled_time),
            ("Người phụ trách", self.assigned_to),
            ("Ghi chú", self.note),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        if not self.title.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Tên công việc là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        scheduled = datetime.combine(
            self.scheduled_date.date().toPython(),
            self.scheduled_time.time().toPython(),
        )
        return {
            "animal_id": self.animal.currentData(),
            "title": self.title.text().strip(),
            "scheduled_at": scheduled.isoformat(timespec="minutes"),
            "assigned_to": self.assigned_to.text().strip(),
            "note": self.note.text().strip(),
        }

class CareChecklistDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        database: Database,
        animals: list[sqlite3.Row],
    ) -> None:
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Checklist chăm sóc và sức khỏe — 25 mục")
        self.setMinimumSize(900, 650)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']}", animal["id"]
            )
        self.checklist_date = QDateEdit(QDate.currentDate())
        self.checklist_date.setCalendarPopup(True)
        self.checklist_date.setDisplayFormat("dd/MM/yyyy")
        self.checked_by = QLineEdit()
        form.addRow("Động vật", self.animal)
        form.addRow("Ngày đánh giá", self.checklist_date)
        form.addRow("Người kiểm tra", self.checked_by)
        layout.addLayout(form)

        self.table = QTableWidget(len(CARE_CHECKLIST_ITEMS), 3)
        self.table.setHorizontalHeaderLabels(["Mục kiểm tra", "Kết quả", "Ghi chú"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.combos: list[QComboBox] = []
        self.notes: list[QTableWidgetItem] = []
        for row, (_, label) in enumerate(CARE_CHECKLIST_ITEMS):
            label_item = QTableWidgetItem(f"{row + 1:02d}. {label}")
            label_item.setFlags(
                label_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 0, label_item)
            result = QComboBox()
            result.addItem("Chọn kết quả", None)
            result.addItem("Đạt", "OK")
            result.addItem("Cần chú ý", "NEEDS_ATTENTION")
            result.addItem("Không áp dụng", "NOT_APPLICABLE")
            self.combos.append(result)
            self.table.setCellWidget(row, 1, result)
            note = QTableWidgetItem()
            self.notes.append(note)
            self.table.setItem(row, 2, note)
        layout.addWidget(self.table, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.animal.currentIndexChanged.connect(self._load_saved)
        self.checklist_date.dateChanged.connect(self._load_saved)
        self._load_saved()

    def _load_saved(self, *_: Any) -> None:
        animal_id = self.animal.currentData()
        if animal_id is None:
            return
        checklist_date = self.checklist_date.date().toString("yyyy-MM-dd")
        saved = self.database.get_care_checklist(animal_id, checklist_date)
        self.checked_by.clear()
        for row, (item_key, _) in enumerate(CARE_CHECKLIST_ITEMS):
            record = saved.get(item_key)
            combo = self.combos[row]
            combo.setCurrentIndex(
                combo.findData(record["status"]) if record else 0
            )
            self.notes[row].setText(record["note"] if record else "")
            if record and record["checked_by"]:
                self.checked_by.setText(record["checked_by"])

    def _validate_and_accept(self) -> None:
        incomplete = [
            index + 1
            for index, combo in enumerate(self.combos)
            if combo.currentData() is None
        ]
        if incomplete:
            shown = ", ".join(str(number) for number in incomplete[:8])
            suffix = "..." if len(incomplete) > 8 else ""
            QMessageBox.warning(
                self,
                "Checklist chưa hoàn tất",
                f"Vui lòng đánh giá đủ 25 mục. Còn thiếu mục: {shown}{suffix}",
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "animal_id": self.animal.currentData(),
            "checklist_date": self.checklist_date.date().toString("yyyy-MM-dd"),
            "checked_by": self.checked_by.text().strip(),
            "items": [
                {
                    "item_key": key,
                    "status": self.combos[index].currentData(),
                    "note": self.notes[index].text().strip(),
                }
                for index, (key, _) in enumerate(CARE_CHECKLIST_ITEMS)
            ],
        }
