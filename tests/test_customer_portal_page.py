from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from app.database import Database
from app.modules.auth.security import hash_password
from app.ui.customer_portal.page import CustomerPortalPage


@pytest.fixture
def application():
    return QApplication.instance() or QApplication([])


def test_staff_can_approve_pending_portal_account_and_issue_invite(
    application, monkeypatch, tmp_path: Path
):
    database = Database(tmp_path / "portal-ui.db")
    admin_id = database.create_initial_admin(
        "portal-ui-admin", "Portal UI Admin", "StrongPass!2026"
    )
    database.set_actor(admin_id)
    customer_id = database.save_customer(
        {
            "customer_code": "CUS-PORTAL-01",
            "name": "Portal Customer",
            "phone": "0900000000",
        }
    )
    invite_customer_id = database.save_customer(
        {"customer_code": "CUS-PORTAL-02", "name": "Invite Customer"}
    )
    salt, password_hash = hash_password("CustomerPass!2026")
    with database.connection:
        database.connection.execute(
            """
            INSERT INTO customer_portal_accounts
                (username, display_name, password_salt, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            ("pending-portal", "Pending Portal", salt, password_hash),
        )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Ok)

    page = CustomerPortalPage(database, can_manage=True)
    assert page.account_table.rowCount() == 1
    page.account_table.selectRow(0)
    page.customer_select.setCurrentIndex(page.customer_select.findData(customer_id))
    page.approve_selected()
    approved = database.connection.execute(
        """
        SELECT status, customer_id FROM customer_portal_accounts
        WHERE username = 'pending-portal'
        """
    ).fetchone()
    assert approved["status"] == "ACTIVE"
    assert approved["customer_id"] == customer_id

    page.invite_customer_select.setCurrentIndex(
        page.invite_customer_select.findData(invite_customer_id)
    )
    page.create_invite()
    invites = database.list_customer_portal_invites("ACTIVE")
    assert len(invites) == 1
    assert invites[0]["customer_id"] == invite_customer_id
    page.close()
    database.close()


def test_portal_staff_page_does_not_load_accounts_without_permission(application):
    class ForbiddenDatabase:
        def list_customer_portal_accounts(self, *_args):
            raise AssertionError("Account list must not be accessed.")

        def list_customer_portal_invites(self, *_args):
            raise AssertionError("Invite list must not be accessed.")

    page = CustomerPortalPage(ForbiddenDatabase(), can_manage=False)

    assert page.account_table.rowCount() == 0
    assert page.invite_table.rowCount() == 0
    assert "sales.manage" in page.status.text()
