import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.auth.constants import ROLE_LABELS
from app.ui.auth.dialogs import CreateUserDialog
from app.ui.common import make_table, set_cell


class UserManagementDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        database: Database,
        actor_id: int,
    ) -> None:
        super().__init__(parent)
        self.database = database
        self.actor_id = actor_id
        self.setWindowTitle("Tài khoản và phân quyền")
        self.resize(760, 460)
        layout = QVBoxLayout(self)
        self.table = make_table(
            ["Tên đăng nhập", "Tên hiển thị", "Vai trò", "Trạng thái"]
        )
        self.table.currentCellChanged.connect(self._selection_changed)
        layout.addWidget(self.table)

        toolbar = QHBoxLayout()
        self.role = QComboBox()
        for key, label in ROLE_LABELS.items():
            self.role.addItem(label, key)
        self.create_button = QPushButton("Tạo tài khoản")
        self.create_button.clicked.connect(self.create_user)
        self.save_role_button = QPushButton("Lưu vai trò")
        self.save_role_button.clicked.connect(self.save_role)
        self.toggle_button = QPushButton("Khóa tài khoản")
        self.toggle_button.clicked.connect(self.toggle_active)
        for widget in (
            self.role,
            self.save_role_button,
            self.toggle_button,
            self.create_button,
        ):
            toolbar.addWidget(widget)
        layout.addLayout(toolbar)
        self.refresh()

    def selected_user_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def refresh(self) -> None:
        selected_id = self.selected_user_id()
        users = self.database.list_users()
        self.table.setRowCount(len(users))
        selected_row = -1
        for row, user in enumerate(users):
            set_cell(self.table, row, 0, user["username"])
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user["id"])
            if user["id"] == selected_id:
                selected_row = row
            set_cell(self.table, row, 1, user["display_name"])
            set_cell(self.table, row, 2, ROLE_LABELS[user["role"]])
            set_cell(
                self.table,
                row,
                3,
                "Đang hoạt động" if user["is_active"] else "Đã khóa",
            )
        if selected_row >= 0:
            self.table.selectRow(selected_row)
        elif users:
            self.table.selectRow(0)
        self._selection_changed()

    def _selection_changed(self, *_: object) -> None:
        user_id = self.selected_user_id()
        row = next(
            (
                index
                for index in range(self.table.rowCount())
                if self.table.item(index, 0).data(Qt.ItemDataRole.UserRole) == user_id
            ),
            -1,
        )
        enabled = user_id is not None
        self.role.setEnabled(enabled)
        self.save_role_button.setEnabled(enabled)
        self.toggle_button.setEnabled(enabled)
        if row >= 0:
            users = self.database.list_users()
            selected = next(
                (user for user in users if user["id"] == user_id), None
            )
            if selected:
                self.role.setCurrentIndex(self.role.findData(selected["role"]))
                self.toggle_button.setText(
                    "Khóa tài khoản"
                    if selected["is_active"]
                    else "Mở khóa tài khoản"
                )
                if selected["id"] == self.actor_id:
                    self.toggle_button.setEnabled(False)
                    self.save_role_button.setEnabled(False)
                else:
                    self.save_role_button.setEnabled(True)

    def create_user(self) -> None:
        dialog = CreateUserDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        try:
            self.database.create_user(
                values["username"],
                values["display_name"],
                values["password"],
                values["role"],
                self.actor_id,
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def save_role(self) -> None:
        user_id = self.selected_user_id()
        if user_id is None:
            return
        role = self.role.currentData()
        try:
            self.database.set_user_role(user_id, role, self.actor_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def toggle_active(self) -> None:
        user_id = self.selected_user_id()
        if user_id is None:
            return
        selected = next(
            (
                user
                for user in self.database.list_users()
                if user["id"] == user_id
            ),
            None,
        )
        if selected is None:
            self.refresh()
            return
        try:
            self.database.set_user_active(
                user_id, not bool(selected["is_active"]), self.actor_id
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh()

    def _show_error(self, error: Exception) -> None:
        message = (
            "Tên đăng nhập đã được sử dụng."
            if isinstance(error, sqlite3.IntegrityError)
            and "users.username" in str(error)
            else str(error)
        )
        QMessageBox.warning(self, "Không thể thực hiện", message)
