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
    QVBoxLayout,
    QWidget,
)

from app.modules.auth.constants import ROLE_LABELS


class AdminSetupDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo tài khoản quản trị")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Đây là tài khoản quản trị đầu tiên của cửa hàng. "
                "Mật khẩu tối thiểu 10 ký tự."
            )
        )
        form = QFormLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Ví dụ: admin")
        self.display_name = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Tên đăng nhập", self.username)
        form.addRow("Tên hiển thị", self.display_name)
        form.addRow("Mật khẩu", self.password)
        form.addRow("Nhập lại mật khẩu", self.confirm_password)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        password = self.password.text()
        if not self.username.text().strip() or not self.display_name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Tên đăng nhập và tên hiển thị là bắt buộc."
            )
            return
        if len(password) < 10:
            QMessageBox.warning(
                self, "Mật khẩu yếu", "Mật khẩu phải có ít nhất 10 ký tự."
            )
            return
        if password != self.confirm_password.text():
            QMessageBox.warning(
                self, "Không khớp", "Hai lần nhập mật khẩu không giống nhau."
            )
            return
        self.accept()

    def values(self) -> dict[str, str]:
        return {
            "username": self.username.text().strip(),
            "display_name": self.display_name.text().strip(),
            "password": self.password.text(),
        }


class LoginDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Đăng nhập — Quản lý thú cưng")
        self.setMinimumWidth(390)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Đăng nhập bằng tài khoản cửa hàng của bạn."))
        form = QFormLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Tên đăng nhập")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self.accept)
        form.addRow("Tên đăng nhập", self.username)
        form.addRow("Mật khẩu", self.password)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Đăng nhập")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def credentials(self) -> tuple[str, str]:
        return self.username.text().strip(), self.password.text()


class CreateUserDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo tài khoản nhân viên")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.username = QLineEdit()
        self.display_name = QLineEdit()
        self.role = QComboBox()
        for key, label in ROLE_LABELS.items():
            self.role.addItem(label, key)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        for label, widget in (
            ("Tên đăng nhập", self.username),
            ("Tên hiển thị", self.display_name),
            ("Vai trò", self.role),
            ("Mật khẩu (tối thiểu 10 ký tự)", self.password),
            ("Nhập lại mật khẩu", self.confirm_password),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if not self.username.text().strip() or not self.display_name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Tên đăng nhập và tên hiển thị là bắt buộc."
            )
            return
        if len(self.password.text()) < 10:
            QMessageBox.warning(
                self, "Mật khẩu yếu", "Mật khẩu phải có ít nhất 10 ký tự."
            )
            return
        if self.password.text() != self.confirm_password.text():
            QMessageBox.warning(
                self, "Không khớp", "Hai lần nhập mật khẩu không giống nhau."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "username": self.username.text().strip(),
            "display_name": self.display_name.text().strip(),
            "password": self.password.text(),
            "role": self.role.currentData(),
        }


class ChangePasswordDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Đổi mật khẩu")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Mật khẩu hiện tại", self.current_password)
        form.addRow("Mật khẩu mới (tối thiểu 10 ký tự)", self.new_password)
        form.addRow("Nhập lại mật khẩu mới", self.confirm_password)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if len(self.new_password.text()) < 10:
            QMessageBox.warning(
                self, "Mật khẩu yếu", "Mật khẩu mới phải có ít nhất 10 ký tự."
            )
            return
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(
                self, "Không khớp", "Hai lần nhập mật khẩu mới không giống nhau."
            )
            return
        self.accept()

    def values(self) -> tuple[str, str]:
        return self.current_password.text(), self.new_password.text()


class AuditLogDialog(QDialog):
    def __init__(self, parent: QWidget, database: Any) -> None:
        from app.ui.common import make_table, set_cell

        super().__init__(parent)
        self.setWindowTitle("Nhật ký thao tác")
        self.resize(1050, 520)
        layout = QVBoxLayout(self)
        self.table = make_table(
            ["Thời điểm", "Tài khoản", "Thao tác", "Loại", "Mã hồ sơ", "Chi tiết"]
        )
        events = database.list_audit_events()
        self.table.setRowCount(len(events))
        for row, event in enumerate(events):
            for column, value in enumerate(
                (
                    event["occurred_at"],
                    event["username"] or "Hệ thống",
                    event["action"],
                    event["entity_type"],
                    event["entity_id"] or "",
                    event["details"],
                )
            ):
                set_cell(self.table, row, column, value)
        layout.addWidget(self.table)
