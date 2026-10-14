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
from app.project_share import ProjectShareServer
from app.remote_database import RemoteDatabase, RemoteDatabaseError
from app.remote_storefront_bridge import RemoteStorefrontBridge
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


def authenticate_remote_user(
    database: RemoteDatabase,
) -> dict[str, object] | None:
    while True:
        dialog = LoginDialog()
        if dialog.exec() != LoginDialog.DialogCode.Accepted:
            return None

        username, password = dialog.credentials()
        try:
            user = database.login(username, password)
        except PermissionError:
            QMessageBox.warning(
                None,
                "Đăng nhập thất bại",
                "Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã bị khóa.",
            )
            continue
        except RemoteDatabaseError as error:
            QMessageBox.warning(
                None,
                "Không kết nối được dịch vụ",
                f"Không thể đăng nhập vào API trung tâm:\n{error}",
            )
            continue

        if user["must_change_password"]:
            change_dialog = ChangePasswordDialog(required=True)
            if change_dialog.exec() != ChangePasswordDialog.DialogCode.Accepted:
                return None
            current_password, new_password = change_dialog.values()
            try:
                database.change_password(
                    int(user["id"]), current_password, new_password, int(user["id"])
                )
            except (PermissionError, RemoteDatabaseError) as error:
                QMessageBox.warning(
                    None, "Không thể đổi mật khẩu", str(error)
                )
                continue
            user["must_change_password"] = False
        return user


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
    database: Database | RemoteDatabase | None = None
    web_bridge: LocalAdminBridge | RemoteStorefrontBridge | None = None
    project_share_server: ProjectShareServer | None = None

    try:
        api_url = os.environ.get("PETCARE_API_URL", "").strip()
        remote_mode = bool(api_url)
        path: Path | None = None
        if remote_mode:
            LOGGER.info("Khởi động %s; API trung tâm đã được cấu hình.", APP_NAME)
            database = RemoteDatabase(api_url)
            current_user = authenticate_remote_user(database)
        else:
            path = database_path()
            LOGGER.info("Khởi động %s; SQLite: %s", APP_NAME, path)
            database = Database(path)
            created_accounts, account_conflicts = database.seed_default_role_accounts()
            if created_accounts:
                LOGGER.warning(
                    "Provisioned %d default role accounts. Change shared/default "
                    "passwords before allowing access from other devices.",
                    len(created_accounts),
                )
            if account_conflicts:
                QMessageBox.warning(
                    None,
                    "Tài khoản mặc định bị trùng vai trò",
                    "Không ghi đè các tài khoản hiện có. Kiểm tra tên đăng nhập sau "
                    "để cấp đúng vai trò: "
                    + ", ".join(account_conflicts),
                )
            if not setup_first_admin(database):
                database.close()
                return 0
            current_user = authenticate_user(database)
        if current_user is None:
            database.close()
            return 0

        user_id = int(current_user["id"])
        database.set_actor(user_id)
        html_root = Path(__file__).resolve().parent / "HTML"
        if remote_mode:
            assert isinstance(database, RemoteDatabase)
            web_bridge = RemoteStorefrontBridge(database.base_url, html_root)
            try:
                bridge_url = web_bridge.start()
                LOGGER.info(
                    "Central API storefront: %s/Web%%20b%%C3%%A1n%%20h%%C3%%A0ng/index.html",
                    bridge_url,
                )
            except (OSError, RuntimeError, TimeoutError) as error:
                LOGGER.warning(
                    "Could not start the central storefront bridge: %s", error
                )
                QMessageBox.warning(
                    None,
                    "Cửa hàng chưa sẵn sàng",
                    "Desktop vẫn kết nối Central API, nhưng chưa thể mở cửa hàng HTML."
                    f"\n\nChi tiết: {error}",
                )
                web_bridge = None
        else:
            database.record_audit(user_id, "LOGIN", "user", user_id)
            assert path is not None
            web_bridge = LocalAdminBridge(
                path,
                html_root,
            )
            try:
                bridge_url = web_bridge.start()
                LOGGER.info(
                    "Admin HTML + SQLite read-only bridge: %s/Trang hỗ trợ/admin_store_management.html",
                    bridge_url,
                )
                LOGGER.info(
                    "SQLite storefront: %s",
                    f"{bridge_url}/Web%20b%C3%A1n%20h%C3%A0ng/index.html",
                )
            except (OSError, TimeoutError) as error:
                LOGGER.warning("Không khởi động được cầu nối admin HTML: %s", error)
                QMessageBox.warning(
                    None,
                    "Admin web chưa sẵn sàng",
                    "Ứng dụng desktop vẫn hoạt động, nhưng giao diện HTML không thể kết nối SQLite. "
                    f"\n\nChi tiết: {error}",
                )
                web_bridge = None
        window = MainWindow(
            database,
            current_user,
            web_base_url=web_bridge.base_url if web_bridge is not None else None,
            project_share_server=(
                ProjectShareServer(path, Path(__file__).resolve().parent)
                if path is not None
                else None
            ),
        )
        project_share_server = window.project_share_server
        window.show()
    except Exception as error:
        if database is not None:
            database.close()
        if web_bridge is not None:
            web_bridge.stop()
        if project_share_server is not None:
            project_share_server.stop()
        show_startup_error(error)
        return 1

    exit_code = application.exec()
    if web_bridge is not None:
        web_bridge.stop()
    if project_share_server is not None:
        project_share_server.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
