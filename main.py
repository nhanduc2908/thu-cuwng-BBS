"""Start the Pet Store Management desktop application."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
from typing import Sequence

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
except ModuleNotFoundError as error:
    if error.name is None or not error.name.startswith("PySide6"):
        raise
    print(
        "PySide6 chưa được cài cho Python đang chạy.\n"
        "Trong PowerShell tại thư mục dự án, chạy:\n"
        "  py -3.13 -m venv .venv\n"
        "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
        "  .\\.venv\\Scripts\\python.exe main.py",
        file=sys.stderr,
    )
    raise SystemExit(1) from error

from app.database import Database
from app.ui.auth.dialogs import AdminSetupDialog, LoginDialog
from app.ui.main_window import MainWindow


APP_NAME = "Quản lý thú cưng"
APP_DATA_DIRECTORY = "PetStoreManagement"
DATABASE_FILENAME = "pet_store.db"

LOGGER = logging.getLogger("pet_store")


def database_path() -> Path:
    """Return the per-user SQLite database location."""
    app_data = os.environ.get("LOCALAPPDATA")
    if app_data:
        base_directory = Path(app_data)
    elif sys.platform == "win32":
        base_directory = Path.home() / "AppData" / "Local"
    else:
        base_directory = Path.home() / ".local" / "share"
    return base_directory / APP_DATA_DIRECTORY / DATABASE_FILENAME


def create_application(arguments: Sequence[str] | None = None) -> QApplication:
    """Create and configure the Qt application."""
    application = QApplication.instance()
    if application is None:
        application = QApplication(list(arguments) if arguments is not None else sys.argv)
    application.setApplicationName(APP_NAME)
    application.setApplicationDisplayName(APP_NAME)
    application.setOrganizationName(APP_DATA_DIRECTORY)
    application.setStyle("Fusion")
    return application


def setup_first_admin(database: Database) -> bool:
    """Prompt for the first administrator; return False when setup is cancelled."""
    if database.user_count() != 0:
        return True

    dialog = AdminSetupDialog()
    if dialog.exec() != AdminSetupDialog.DialogCode.Accepted:
        return False

    credentials = dialog.values()
    database.create_initial_admin(
        credentials["username"],
        credentials["display_name"],
        credentials["password"],
    )
    return True


def authenticate_user(database: Database) -> dict[str, object] | None:
    """Keep prompting until login succeeds or the user exits the login dialog."""
    while True:
        dialog = LoginDialog()
        if dialog.exec() != LoginDialog.DialogCode.Accepted:
            return None

        username, password = dialog.credentials()
        user = database.authenticate(username, password)
        if user is not None:
            return user

        database.record_audit(
            None,
            "LOGIN_FAILED",
            "user",
            details=f"username={username[:64]}",
        )
        QMessageBox.warning(
            None,
            "Đăng nhập thất bại",
            "Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã bị khóa.",
        )


def show_startup_error(error: Exception) -> None:
    LOGGER.exception("Không thể khởi động ứng dụng", exc_info=error)
    QMessageBox.critical(
        None,
        "Không thể khởi động",
        f"Ứng dụng không thể khởi tạo:\n{error}",
    )


def main(arguments: Sequence[str] | None = None) -> int:
    """Initialize storage and authentication, then run the main window."""
    logging.basicConfig(level=logging.INFO)
    application = create_application(arguments)
    database: Database | None = None

    try:
        database = Database(database_path())
        if not setup_first_admin(database):
            database.close()
            return 0

        current_user = authenticate_user(database)
        if current_user is None:
            database.close()
            return 0

        user_id = int(current_user["id"])
        database.set_actor(user_id)
        database.record_audit(user_id, "LOGIN", "user", user_id)

        window = MainWindow(database, current_user)
        window.show()
    except Exception as error:
        if database is not None:
            database.close()
        show_startup_error(error)
        return 1

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
