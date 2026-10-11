from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table


class CustomerPortalPage(QWidget):
    def __init__(self, database: Database, can_manage: bool) -> None:
        super().__init__()
        self.database = database
        self.can_manage = can_manage
        self.accounts: list[sqlite3.Row] = []
        self.invites: list[sqlite3.Row] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(
            QLabel("Tài khoản portal khách hàng", objectName="pageTitle")
        )
        explanation = QLabel(
            "Duyệt đăng ký bằng cách gắn với hồ sơ khách hàng đã tồn tại, hoặc cấp "
            "mã mời một lần cho hồ sơ đó. Không tạo hồ sơ khách hàng từ dữ liệu tự "
            "đăng ký. Chỉ gửi mã mời cho đúng khách hàng."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self.status = QLabel("Đang tải danh sách tài khoản portal.")
        self.status.setObjectName("pageSubtitle")
        layout.addWidget(self.status)

        self.tabs = QTabWidget()
        pending_tab = QWidget()
        pending_layout = QVBoxLayout(pending_tab)
        self.customer_select = QComboBox()
        customer_row = QHBoxLayout()
        customer_row.addWidget(QLabel("Liên kết với hồ sơ khách hàng"))
        customer_row.addWidget(self.customer_select, 1)
        self.approve_button = QPushButton("Duyệt & liên kết")
        self.approve_button.setObjectName("primaryButton")
        self.approve_button.clicked.connect(self.approve_selected)
        customer_row.addWidget(self.approve_button)
        self.reject_button = QPushButton("Từ chối đăng ký")
        self.reject_button.clicked.connect(self.reject_selected)
        customer_row.addWidget(self.reject_button)
        pending_layout.addLayout(customer_row)
        self.account_table = make_table(
            ["Tên đăng nhập", "Tên hiển thị", "Gửi lúc", "Trạng thái"]
        )
        self.account_table.currentCellChanged.connect(self._update_controls)
        pending_layout.addWidget(self.account_table)
        self.tabs.addTab(pending_tab, "Đăng ký chờ duyệt")

        invite_tab = QWidget()
        invite_layout = QVBoxLayout(invite_tab)
        issue_row = QHBoxLayout()
        issue_row.addWidget(QLabel("Cấp lời mời cho hồ sơ"))
        self.invite_customer_select = QComboBox()
        issue_row.addWidget(self.invite_customer_select, 1)
        self.create_invite_button = QPushButton(
            "Tạo mã mời (24 giờ)", objectName="primaryButton"
        )
        self.create_invite_button.clicked.connect(self.create_invite)
        issue_row.addWidget(self.create_invite_button)
        self.expire_invite_button = QPushButton("Hủy mã đang chọn")
        self.expire_invite_button.clicked.connect(self.expire_selected_invite)
        issue_row.addWidget(self.expire_invite_button)
        invite_layout.addLayout(issue_row)
        self.invite_table = make_table(
            ["Mã", "Khách hàng", "Tạo lúc", "Hết hạn", "Trạng thái"]
        )
        self.invite_table.currentCellChanged.connect(self._update_controls)
        invite_layout.addWidget(self.invite_table)
        self.tabs.addTab(invite_tab, "Mã mời")
        layout.addWidget(self.tabs, 1)

        self.set_manage_enabled(can_manage)
        self.refresh()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.can_manage = enabled
        for widget in (
            self.customer_select,
            self.approve_button,
            self.reject_button,
            self.invite_customer_select,
            self.create_invite_button,
            self.expire_invite_button,
        ):
            widget.setEnabled(enabled)

    def refresh(self, *_: object) -> None:
        if not self.can_manage:
            self.status.setText(
                "Cần quyền sales.manage và tài khoản nhân viên để quản lý portal."
            )
            self.account_table.setRowCount(0)
            self.invite_table.setRowCount(0)
            return
        try:
            self.accounts = self.database.list_customer_portal_accounts("PENDING")
            self.invites = self.database.list_customer_portal_invites("ALL")
            customers = self.database.list_customers()
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.status.setText(f"Không thể tải danh sách portal: {error}")
            self.account_table.setRowCount(0)
            self.invite_table.setRowCount(0)
            return

        self.customer_select.clear()
        self.invite_customer_select.clear()
        for customer in customers:
            label = f"{customer['customer_code']} · {customer['name']}"
            self.customer_select.addItem(label, int(customer["id"]))
            self.invite_customer_select.addItem(label, int(customer["id"]))

        self.account_table.setRowCount(len(self.accounts))
        for row_index, account in enumerate(self.accounts):
            self._set_row(
                self.account_table,
                row_index,
                (
                    account["username"],
                    account["display_name"],
                    account["created_at"],
                    account["status"],
                ),
                int(account["id"]),
            )
        self.invite_table.setRowCount(len(self.invites))
        for row_index, invite in enumerate(self.invites):
            self._set_row(
                self.invite_table,
                row_index,
                (
                    invite["id"],
                    f"{invite['customer_code']} · {invite['customer_name']}",
                    invite["created_at"],
                    invite["expires_at"],
                    invite["status"],
                ),
                int(invite["id"]),
            )
        self.status.setText(
            f"{len(self.accounts)} đăng ký chờ duyệt · "
            f"{sum(invite['status'] == 'ACTIVE' for invite in self.invites)} mã mời đang hoạt động"
        )
        self._update_controls()

    @staticmethod
    def _set_row(
        table: QTableWidget, row: int, values: tuple[object, ...], record_id: int
    ) -> None:
        for column, value in enumerate(values):
            item = QTableWidgetItem("" if value is None else str(value))
            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole, record_id)
            table.setItem(row, column, item)

    def _selected_id(self, table: QTableWidget) -> int | None:
        row = table.currentRow()
        if row < 0:
            return None
        item = table.item(row, 0)
        if item is None:
            return None
        value = item.data(Qt.ItemDataRole.UserRole)
        return int(value) if value is not None else None

    def _update_controls(self, *_: object) -> None:
        selected_account = self._selected_id(self.account_table)
        selected_invite = self._selected_id(self.invite_table)
        self.approve_button.setEnabled(
            self.can_manage
            and selected_account is not None
            and self.customer_select.count() > 0
        )
        self.reject_button.setEnabled(self.can_manage and selected_account is not None)
        active_invites = {
            int(invite["id"])
            for invite in self.invites
            if invite["status"] == "ACTIVE"
        }
        self.expire_invite_button.setEnabled(
            self.can_manage and selected_invite in active_invites
        )
        self.create_invite_button.setEnabled(
            self.can_manage and self.invite_customer_select.count() > 0
        )

    def approve_selected(self) -> None:
        account_id = self._selected_id(self.account_table)
        customer_id = self.customer_select.currentData()
        if account_id is None or customer_id is None:
            return
        confirmation = QMessageBox.question(
            self,
            "Xác nhận liên kết",
            "Duyệt tài khoản và cho phép tài khoản này xem dữ liệu của hồ sơ khách hàng đã chọn?",
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            if not self.database.approve_customer_portal_account(
                account_id, int(customer_id)
            ):
                raise ValueError("Đăng ký không còn ở trạng thái chờ duyệt.")
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể duyệt tài khoản", str(error))
            return
        self.refresh()

    def reject_selected(self) -> None:
        account_id = self._selected_id(self.account_table)
        if account_id is None:
            return
        confirmation = QMessageBox.question(
            self,
            "Từ chối đăng ký",
            "Bạn có chắc muốn từ chối đăng ký portal đã chọn?",
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            if not self.database.reject_customer_portal_account(account_id):
                raise ValueError("Đăng ký không còn ở trạng thái chờ duyệt.")
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể từ chối đăng ký", str(error))
            return
        self.refresh()

    def create_invite(self) -> None:
        customer_id = self.invite_customer_select.currentData()
        if customer_id is None:
            return
        try:
            invite = self.database.create_customer_portal_invite(int(customer_id))
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tạo mã mời", str(error))
            return
        message = QMessageBox(self)
        message.setWindowTitle("Mã mời được tạo")
        message.setIcon(QMessageBox.Icon.Information)
        message.setText(
            "Gửi mã một lần này riêng cho khách hàng đã chọn. Mã chỉ hiển thị lần này "
            "và hết hạn sau 24 giờ."
        )
        message.setInformativeText(
            f"{invite['invite_code']}\nHết hạn: {invite['expires_at']}"
        )
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message.exec()
        self.refresh()

    def expire_selected_invite(self) -> None:
        invite_id = self._selected_id(self.invite_table)
        if invite_id is None:
            return
        confirmation = QMessageBox.question(
            self,
            "Hủy mã mời",
            "Hủy mã mời đang hoạt động đã chọn?",
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            if not self.database.expire_customer_portal_invite(invite_id):
                raise ValueError("Mã mời không còn hoạt động.")
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể hủy mã mời", str(error))
            return
        self.refresh()
