import sqlite3
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table, set_cell


class CageDialog(QDialog):
    def __init__(self, parent: QWidget, cage: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật chuồng" if cage else "Thêm chuồng")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.code = QLineEdit()
        self.code.setPlaceholderText("Ví dụ: C-A01")
        self.name = QLineEdit()
        self.area = QLineEdit()
        self.area.setPlaceholderText("Ví dụ: Khu A, tầng 1")
        self.accepted_species = QComboBox()
        self.accepted_species.setEditable(True)
        self.accepted_species.addItems(
            ("", "Chó", "Mèo", "Chim", "Thỏ", "Hamster", "Cá", "Bò sát")
        )
        self.capacity = QSpinBox()
        self.capacity.setRange(1, 100000)
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)

        for label, widget in (
            ("Mã chuồng *", self.code),
            ("Tên chuồng *", self.name),
            ("Khu vực", self.area),
            ("Loài tiếp nhận", self.accepted_species),
            ("Sức chứa *", self.capacity),
            ("Ghi chú", self.description),
        ):
            form.addRow(label, widget)
        layout.addWidget(
            QLabel("Để trống loài tiếp nhận nếu chuồng dùng được cho mọi loài.")
        )
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if cage:
            self.code.setText(cage["cage_code"])
            self.name.setText(cage["name"])
            self.area.setText(cage["area"])
            self.accepted_species.setCurrentText(cage["accepted_species"])
            self.capacity.setValue(cage["capacity"])
            self.description.setPlainText(cage["description"])

    def _validate_and_accept(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Mã chuồng và tên chuồng là bắt buộc."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "cage_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "area": self.area.text().strip(),
            "accepted_species": self.accepted_species.currentText().strip(),
            "capacity": self.capacity.value(),
            "description": self.description.toPlainText().strip(),
        }


class AssignAnimalDialog(QDialog):
    def __init__(self, parent: QWidget, animals: list[sqlite3.Row]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gán/chuyển động vật vào chuồng")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.animal = QComboBox()
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']} ({animal['species']})",
                animal["id"],
            )
        self.note = QLineEdit()
        self.note.setPlaceholderText("Lý do chuyển chuồng (nếu có)")
        form.addRow("Động vật", self.animal)
        form.addRow("Ghi chú", self.note)
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
            "note": self.note.text().strip(),
        }


class CageHistoryDialog(QDialog):
    def __init__(
        self, parent: QWidget, database: Database, cage: sqlite3.Row
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Lịch sử chuồng — {cage['cage_code']}")
        self.resize(850, 420)
        layout = QVBoxLayout(self)
        self.table = make_table(
            ["Mã động vật", "Tên", "Loài", "Ngày vào", "Ngày chuyển đi", "Ghi chú"]
        )
        history = database.list_cage_history(cage["id"])
        self.table.setRowCount(len(history))
        for row, assignment in enumerate(history):
            for column, value in enumerate(
                (
                    assignment["animal_code"],
                    assignment["animal_name"],
                    assignment["species"],
                    assignment["assigned_at"],
                    assignment["released_at"] or "Đang ở",
                    assignment["note"],
                )
            ):
                set_cell(self.table, row, column, value)
        layout.addWidget(self.table)
