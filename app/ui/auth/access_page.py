from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.auth.constants import ROLE_LABELS


class AccessPage(QWidget):
    def __init__(
        self,
        database: Database,
        current_user: dict[str, Any],
        can_manage_users: bool,
        can_view_audit: bool,
        manage_users: Callable[[], None],
        view_audit: Callable[[], None],
    ) -> None:
        super().__init__()
        self.database = database
        self.current_user = current_user
        self.manage_users_callback = manage_users
        self.view_audit_callback = view_audit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(
            QLabel("Tài khoản, vai trò & kiểm soát", objectName="pageTitle")
        )
        layout.addWidget(
            QLabel(
                "Quản lý danh tính người dùng và xem lại các thao tác đã được ghi nhận."
            )
        )

        summary = QFrame(objectName="statCard")
        summary_layout = QVBoxLayout(summary)
        self.identity = QLabel()
        self.identity.setObjectName("statValue")
        self.identity.setWordWrap(True)
        summary_layout.addWidget(self.identity)
        self.role_description = QLabel()
        self.role_description.setWordWrap(True)
        summary_layout.addWidget(self.role_description)
        layout.addWidget(summary)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.users_button = QPushButton(
            "Quản lý tài khoản & vai trò", objectName="primaryButton"
        )
        self.users_button.setVisible(can_manage_users)
        self.users_button.clicked.connect(self.manage_users_callback)
        self.audit_button = QPushButton("Mở nhật ký thao tác")
        self.audit_button.setVisible(can_view_audit)
        self.audit_button.clicked.connect(self.view_audit_callback)
        actions.addWidget(self.users_button)
        actions.addWidget(self.audit_button)
        layout.addLayout(actions)

        self.permissions_note = QLabel(
            "Quyền truy cập được xác định theo vai trò và kiểm tra lại ở tầng dữ liệu."
        )
        self.permissions_note.setWordWrap(True)
        layout.addWidget(self.permissions_note)
        layout.addStretch(1)
        self.refresh()

    def refresh(self, *_: object) -> None:
        role = str(self.current_user.get("role", ""))
        display_name = str(
            self.current_user.get("display_name", self.current_user.get("username", ""))
        )
        self.identity.setText(display_name)
        self.role_description.setText(
            f"Đang đăng nhập với vai trò: {ROLE_LABELS.get(role, role)}"
        )
