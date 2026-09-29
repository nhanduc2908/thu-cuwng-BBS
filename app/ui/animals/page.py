import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.animals.constants import ANIMAL_STATUSES
from app.ui.animals.dialogs import AnimalDialog
from app.ui.common import STATUS_LABELS, make_table, notify_error, set_cell
from app.ui.photo_preview import show_photo_preview


class AnimalsPage(QWidget):
    def __init__(self, database: Database, on_change: Any) -> None:
        super().__init__()
        self.database = database
        self.on_change = on_change
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm theo mã, tên, loài hoặc giống...")
        self.search.textChanged.connect(self.refresh)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tất cả trạng thái", None)
        for status in ANIMAL_STATUSES:
            self.status_filter.addItem(STATUS_LABELS[status], status)
        self.status_filter.currentIndexChanged.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        header = QHBoxLayout()
        title = QLabel("Quản lý động vật", objectName="pageTitle")
        header.addWidget(title)
        header.addStretch()
        add_button = QPushButton("+ Thêm động vật", objectName="primaryButton")
        add_button.clicked.connect(self.add_animal)
        self.add_button = add_button
        header.addWidget(add_button)
        layout.addLayout(header)

        filters = QHBoxLayout()
        filters.addWidget(self.search, 2)
        filters.addWidget(self.status_filter, 1)
        layout.addLayout(filters)
        self.table = make_table(
            [
                "Mã",
                "Tên",
                "Loài / Giống",
                "Giới tính",
                "Cân nặng",
                "Giá bán",
                "Trạng thái",
                "Sức khỏe",
                "Tiếp nhận",
            ]
        )
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        buttons.addStretch()
        edit_button = QPushButton("Chỉnh sửa")
        edit_button.clicked.connect(self.edit_animal)
        self.edit_button = edit_button
        delete_button = QPushButton("Xóa")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.delete_animal)
        self.delete_button = delete_button
        self.photo_button = QPushButton("Xem ảnh nhận bé")
        self.photo_button.clicked.connect(self.show_intake_photo)
        self.photo_button.setEnabled(False)
        buttons.addWidget(self.photo_button)
        buttons.addWidget(edit_button)
        buttons.addWidget(delete_button)
        layout.addLayout(buttons)
        self.table.doubleClicked.connect(self.edit_animal)
        self.table.currentCellChanged.connect(self._selection_changed)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.add_button.setVisible(enabled)
        self.edit_button.setVisible(enabled)
        self.delete_button.setVisible(enabled)

    def refresh(self, *_: Any) -> None:
        animals = self.database.list_animals(
            self.search.text(), self.status_filter.currentData()
        )
        self.table.setRowCount(len(animals))
        for row_number, animal in enumerate(animals):
            set_cell(self.table, row_number, 0, animal["animal_code"])
            self.table.item(row_number, 0).setData(
                Qt.ItemDataRole.UserRole, animal["id"]
            )
            set_cell(self.table, row_number, 1, animal["name"])
            breed = f" / {animal['breed']}" if animal["breed"] else ""
            set_cell(self.table, row_number, 2, f"{animal['species']}{breed}")
            set_cell(self.table, row_number, 3, animal["gender"])
            weight = f"{animal['weight']:g} kg" if animal["weight"] is not None else "—"
            set_cell(self.table, row_number, 4, weight)
            set_cell(self.table, row_number, 5, f"{animal['sale_price']:,.0f} ₫")
            set_cell(self.table, row_number, 6, STATUS_LABELS[animal["status"]])
            set_cell(self.table, row_number, 7, animal["health_status"])
            set_cell(
                self.table,
                row_number,
                8,
                "Đã nhận"
                if animal["received_at"]
                else "Không qua quy trình nhập",
            )
        self._selection_changed()

    def selected_animal_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _selection_changed(self, *_: Any) -> None:
        animal_id = self.selected_animal_id()
        animal = self.database.get_animal(animal_id) if animal_id else None
        self.photo_button.setEnabled(
            animal is not None and bool(animal["received_at"])
        )

    def show_intake_photo(self) -> None:
        animal_id = self.selected_animal_id()
        if animal_id is None:
            return
        receipt = self.database.get_intake_receipt(animal_id)
        if receipt is None:
            QMessageBox.information(
                self, "Chưa có ảnh", "Hồ sơ này chưa có chứng từ ảnh tiếp nhận."
            )
            return
        animal = self.database.get_animal(animal_id)
        if animal is None:
            self.refresh()
            return
        try:
            show_photo_preview(
                self,
                f"Ảnh tiếp nhận — {animal['animal_code']} · {animal['name']}",
                receipt["photo_data"],
            )
        except ValueError as error:
            notify_error(self, error)

    def add_animal(self) -> None:
        dialog = AnimalDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save(dialog.values())

    def edit_animal(self, *_: Any) -> None:
        animal_id = self.selected_animal_id()
        if animal_id is None:
            QMessageBox.information(self, "Chọn động vật", "Chọn một dòng để chỉnh sửa.")
            return
        animal = self.database.get_animal(animal_id)
        if animal is None:
            QMessageBox.warning(self, "Không tìm thấy", "Hồ sơ động vật không còn tồn tại.")
            self.refresh()
            return
        dialog = AnimalDialog(self, animal)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save(dialog.values(), animal_id)

    def _save(self, values: dict[str, Any], animal_id: int | None = None) -> None:
        try:
            self.database.save_animal(values, animal_id)
        except (sqlite3.Error, ValueError) as error:
            notify_error(self, error)
            return
        self.refresh()
        self.on_change()

    def delete_animal(self) -> None:
        animal_id = self.selected_animal_id()
        if animal_id is None:
            QMessageBox.information(self, "Chọn động vật", "Chọn một dòng để xóa.")
            return
        confirmation = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa hồ sơ động vật này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            self.database.delete_animal(animal_id)
        except sqlite3.Error as error:
            notify_error(self, error)
            return
        self.refresh()
        self.on_change()
