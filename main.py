"""Start the PetCare desktop application and initialize local authentication."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import sqlite3
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
from app.web_bridge import LocalAdminBridge
from app.ui.auth.dialogs import ChangePasswordDialog, LoginDialog
from app.ui.main_window import MainWindow


APP_NAME = "PetCare - Quản lý thú cưng"
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
    """Create the documented first-run account with mandatory password rotation."""
    if database.user_count() != 0:
        return True

    database.create_default_admin()
    QMessageBox.information(
        None,
        "Tài khoản đã tạo",
        "Tài khoản lần đầu: admin / admin.\n"
        "Bạn sẽ phải đặt mật khẩu mới ngay sau khi đăng nhập.",
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
            if user["must_change_password"]:
                change_dialog = ChangePasswordDialog(required=True)
                if change_dialog.exec() != ChangePasswordDialog.DialogCode.Accepted:
                    return None
                current_password, new_password = change_dialog.values()
                try:
                    database.change_password(
                        int(user["id"]),
                        current_password,
                        new_password,
                        int(user["id"]),
                    )
                except (ValueError, sqlite3.Error) as error:
                    QMessageBox.warning(
                        None, "Không thể đổi mật khẩu", str(error)
                    )
                    continue
                user["must_change_password"] = False
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
    LOGGER.error(
        "Không thể khởi động ứng dụng",
        exc_info=(type(error), error, error.__traceback__),
    )
    QMessageBox.critical(
        None,
        "Không thể khởi động",
        f"Ứng dụng không thể khởi tạo:\n{error}",
    )


def main(arguments: Sequence[str] | None = None) -> int:
    """Initialize storage and authentication, then run the main window."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    logging.basicConfig(level=logging.INFO)
    command_arguments = list(arguments) if arguments is not None else sys.argv[1:]
    if command_arguments == ["--reset-admin"]:
        database: Database | None = None
        try:
            path = database_path()
            if not path.is_file():
                raise FileNotFoundError(
                    f"Không tìm thấy cơ sở dữ liệu hiện có: {path}"
                )
            database = Database(path)
            database.reset_admin_login("admin")
        except Exception as error:
            print(f"Không thể khôi phục tài khoản admin: {error}", file=sys.stderr)
            return 1
        finally:
            if database is not None:
                database.close()
        print(
            "Đã đặt lại tài khoản quản trị về admin/admin. "
            "Khi đăng nhập, ứng dụng sẽ yêu cầu đặt mật khẩu mới."
        )
        return 0

    application = create_application(arguments)
    database: Database | None = None
    web_bridge: LocalAdminBridge | None = None

    try:
        path = database_path()
        LOGGER.info("Khởi động %s; SQLite: %s", APP_NAME, path)
        database = Database(path)
        database.ensure_default_admin_credentials()
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

        web_bridge = LocalAdminBridge(path, Path(__file__).resolve().parent / "HTML")
        try:
            bridge_url = web_bridge.start()
            LOGGER.info("Admin HTML + SQLite read-only bridge: %s/admin_store_management.html", bridge_url)
        except (OSError, TimeoutError) as error:
            LOGGER.warning("Không khởi động được cầu nối admin HTML: %s", error)
            QMessageBox.warning(
                None,
                "Admin web chưa sẵn sàng",
                "Ứng dụng desktop vẫn hoạt động, nhưng giao diện HTML không thể kết nối SQLite. "
                f"\n\nChi tiết: {error}",
            )
            web_bridge = None

        window = MainWindow(database, current_user)
        window.show()
    except Exception as error:
        if database is not None:
            database.close()
        if web_bridge is not None:
            web_bridge.stop()
        show_startup_error(error)
        return 1

    exit_code = application.exec()
    if web_bridge is not None:
        web_bridge.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
