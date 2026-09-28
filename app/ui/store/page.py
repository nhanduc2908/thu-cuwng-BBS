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
from app.ui.common import STATUS_LABELS, make_table, set_cell
from app.ui.store.dialogs import (
    AssignAnimalDialog,
    CageDialog,
    CageHistoryDialog,
)


class StorePage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.manage_enabled = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)

        header = QHBoxLayout()
        header.addWidget(QLabel("Quản lý chuồng trại", objectName="pageTitle"))
        header.addStretch()
        add_button = QPushButton("+ Thêm chuồng", objectName="primaryButton")
        add_button.clicked.connect(self.add_cage)
        self.add_button = add_button
        header.addWidget(add_button)
        layout.addLayout(header)

        layout.addWidget(
            QLabel("Sức chứa được kiểm tra tự động khi gán hoặc chuyển động vật.")
        )
        self.cages_table = make_table(
            ["Mã", "Tên chuồng", "Khu vực", "Loài", "Đang ở", "Sức chứa", "Trạng thái"]
        )
        self.cages_table.currentCellChanged.connect(self._selection_changed)
        layout.addWidget(self.cages_table, 3)

        cage_buttons = QHBoxLayout()
        cage_buttons.addStretch()
        self.edit_button = QPushButton("Sửa chuồng")
        self.edit_button.clicked.connect(self.edit_cage)
        self.delete_button = QPushButton("Xóa chuồng")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_cage)
        self.active_button = QPushButton("Ngừng hoạt động")
        self.active_button.clicked.connect(self.toggle_cage_active)
        self.history_button = QPushButton("Lịch sử chuồng")
        self.history_button.clicked.connect(self.show_cage_history)
        cage_buttons.addWidget(self.edit_button)
        cage_buttons.addWidget(self.active_button)
        cage_buttons.addWidget(self.history_button)
        cage_buttons.addWidget(self.delete_button)
        layout.addLayout(cage_buttons)

        occupants_header = QHBoxLayout()
        occupants_header.addWidget(
            QLabel("Động vật đang ở chuồng", objectName="sectionTitle")
        )
        occupants_header.addStretch()
        self.assign_button = QPushButton("Gán/chuyển động vật", objectName="primaryButton")
        self.assign_button.clicked.connect(self.assign_animal)
        self.unassign_button = QPushButton("Tháo khỏi chuồng")
        self.unassign_button.clicked.connect(self.unassign_animal)
        occupants_header.addWidget(self.assign_button)
        occupants_header.addWidget(self.unassign_button)
        layout.addLayout(occupants_header)

        self.animals_table = make_table(["Mã", "Tên", "Loài", "Trạng thái", "Ngày vào"])
        layout.addWidget(self.animals_table, 2)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.manage_enabled = enabled
        self.add_button.setVisible(enabled)
        self.edit_button.setVisible(enabled)
        self.delete_button.setVisible(enabled)
        self.active_button.setVisible(enabled)
        self.assign_button.setVisible(enabled)
        self.unassign_button.setVisible(enabled)
        self.history_button.setVisible(self._has_selected_cage())

    def _has_selected_cage(self) -> bool:
        return self.selected_cage_id() is not None

    def selected_cage_id(self) -> int | None:
        row = self.cages_table.currentRow()
        if row < 0 or self.cages_table.item(row, 0) is None:
            return None
        return self.cages_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def selected_animal_id(self) -> int | None:
        row = self.animals_table.currentRow()
        if row < 0 or self.animals_table.item(row, 0) is None:
            return None
        return self.animals_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def refresh(self, *_: Any) -> None:
        cages = self.database.list_cages()
        self.cages_table.setRowCount(len(cages))
        for row, cage in enumerate(cages):
            set_cell(self.cages_table, row, 0, cage["cage_code"])
            self.cages_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, cage["id"]
            )
            set_cell(self.cages_table, row, 1, cage["name"])
            set_cell(self.cages_table, row, 2, cage["area"])
            set_cell(
                self.cages_table,
                row,
                3,
                cage["accepted_species"] or "Mọi loài",
            )
            count = cage["assigned_count"]
            capacity = cage["capacity"]
            set_cell(self.cages_table, row, 4, count)
            set_cell(self.cages_table, row, 5, capacity)
            status = (
                "Ngừng hoạt động"
                if not cage["is_active"]
                else "Đầy"
                if count >= capacity
                else "Còn chỗ"
            )
            set_cell(self.cages_table, row, 6, status)

        if cages and self.cages_table.currentRow() < 0:
            self.cages_table.selectRow(0)
        self._selection_changed()

    def _selection_changed(self, *_: Any) -> None:
        cage_id = self.selected_cage_id()
        self.animals_table.setRowCount(0)
        enabled = cage_id is not None
        self.edit_button.setEnabled(enabled and self.manage_enabled)
        self.delete_button.setEnabled(enabled and self.manage_enabled)
        self.active_button.setEnabled(enabled and self.manage_enabled)
        self.history_button.setEnabled(enabled)
        if cage_id is None:
            self.assign_button.setEnabled(False)
            return
        cage = self.database.get_cage(cage_id)
        self.assign_button.setEnabled(
            bool(cage and cage["is_active"] and self.manage_enabled)
        )
        self.active_button.setText(
            "Ngừng hoạt động" if cage and cage["is_active"] else "Kích hoạt lại"
        )
        for row, animal in enumerate(self.database.list_cage_animals(cage_id)):
            self.animals_table.insertRow(row)
            set_cell(self.animals_table, row, 0, animal["animal_code"])
            self.animals_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, animal["id"]
            )
            set_cell(self.animals_table, row, 1, animal["name"])
            set_cell(self.animals_table, row, 2, animal["species"])
            set_cell(
                self.animals_table,
                row,
                3,
                STATUS_LABELS.get(animal["status"], animal["status"]),
            )
            set_cell(self.animals_table, row, 4, animal["assigned_at"])

    def add_cage(self) -> None:
        dialog = CageDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_cage(dialog.values())

    def edit_cage(self) -> None:
        cage_id = self.selected_cage_id()
        if cage_id is None:
            QMessageBox.information(self, "Chọn chuồng", "Chọn chuồng cần cập nhật.")
            return
        cage = self.database.get_cage(cage_id)
        if cage is None:
            QMessageBox.warning(self, "Không tìm thấy", "Chuồng không còn tồn tại.")
            self.refresh()
            return
        dialog = CageDialog(self, cage)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_cage(dialog.values(), cage_id)

    def _save_cage(self, values: dict[str, Any], cage_id: int | None = None) -> None:
        try:
            self.database.save_cage(values, cage_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def delete_cage(self) -> None:
        cage_id = self.selected_cage_id()
        if cage_id is None:
            return
        answer = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Xóa chuồng này? Chuồng có động vật hoặc lịch sử phân chuồng sẽ được giữ lại.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.database.delete_cage(cage_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def toggle_cage_active(self) -> None:
        cage_id = self.selected_cage_id()
        if cage_id is None:
            return
        cage = self.database.get_cage(cage_id)
        if cage is None:
            self.refresh()
            return
        try:
            self.database.set_cage_active(cage_id, not bool(cage["is_active"]))
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def show_cage_history(self) -> None:
        cage_id = self.selected_cage_id()
        if cage_id is None:
            return
        cage = self.database.get_cage(cage_id)
        if cage is None:
            self.refresh()
            return
        CageHistoryDialog(self, self.database, cage).exec()

    def assign_animal(self) -> None:
        cage_id = self.selected_cage_id()
        if cage_id is None:
            QMessageBox.information(self, "Chọn chuồng", "Chọn chuồng nhận động vật.")
            return
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self,
                "Chưa có động vật",
                "Hãy tạo hồ sơ động vật trước khi phân chuồng.",
            )
            return
        dialog = AssignAnimalDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        try:
            self.database.assign_animal_to_cage(
                values["animal_id"], cage_id, values["note"]
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def unassign_animal(self) -> None:
        animal_id = self.selected_animal_id()
        if animal_id is None:
            QMessageBox.information(
                self,
                "Chọn động vật",
                "Chọn động vật đang ở chuồng cần tháo.",
            )
            return
        try:
            self.database.unassign_animal_from_cage(animal_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def _show_error(self, error: Exception) -> None:
        message = str(error)
        if isinstance(error, sqlite3.IntegrityError) and "cages.cage_code" in message:
            message = "Mã chuồng đã tồn tại."
        QMessageBox.warning(self, "Không thể thực hiện", message)
