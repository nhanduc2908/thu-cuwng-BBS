import sqlite3
from typing import Any

from app.modules.auth.constants import ROLE_PERMISSIONS
from app.modules.auth.security import hash_password, verify_password


class AuthRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def user_count(self) -> int:
        return int(
            self.connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        )

    def list_users(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT id, username, display_name, role, is_active, created_at
            FROM users ORDER BY username COLLATE NOCASE
            """
        ).fetchall()

    def create_user(
        self,
        username: str,
        display_name: str,
        password: str,
        role: str,
    ) -> int:
        normalized_username = username.strip().casefold()
        if not normalized_username or not display_name.strip():
            raise ValueError("Tên đăng nhập và tên hiển thị là bắt buộc.")
        if len(normalized_username) > 64:
            raise ValueError("Tên đăng nhập không được vượt quá 64 ký tự.")
        if role not in ROLE_PERMISSIONS:
            raise ValueError("Vai trò được chọn không hợp lệ.")
        salt, password_hash = hash_password(password)
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO users
                    (username, display_name, password_salt, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    normalized_username,
                    display_name.strip(),
                    salt,
                    password_hash,
                    role,
                ),
            )
            return int(cursor.lastrowid)

    def create_initial_admin(
        self, username: str, display_name: str, password: str
    ) -> int:
        if self.user_count() != 0:
            raise ValueError("Tài khoản quản trị ban đầu đã được thiết lập.")
        user_id = self.create_user(username, display_name, password, "ADMIN")
        with self.connection:
            self.connection.execute(
                """
                UPDATE users SET password_changed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (user_id,),
            )
        return user_id

    def create_default_admin(self) -> int:
        if self.user_count() != 0:
            raise ValueError("Tài khoản quản trị ban đầu đã được thiết lập.")
        salt, password_hash = hash_password("admin", allow_short=True)
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO users
                    (username, display_name, password_salt, password_hash, role,
                     must_change_password)
                VALUES ('admin', 'Quản trị cửa hàng', ?, ?, 'ADMIN', 1)
                """,
                (salt, password_hash),
            )
            return int(cursor.lastrowid)

    def reset_admin_password(self, username: str = "admin") -> int:
        normalized_username = username.strip().casefold()
        if not normalized_username:
            raise ValueError("Tên đăng nhập quản trị không được để trống.")
        user = self.connection.execute(
            """
            SELECT id FROM users
            WHERE username = ? AND role = 'ADMIN'
            """,
            (normalized_username,),
        ).fetchone()
        if user is None:
            raise ValueError(
                f"Không tìm thấy tài khoản quản trị '{normalized_username}'."
            )
        salt, password_hash = hash_password("admin", allow_short=True)
        with self.connection:
            self.connection.execute(
                """
                UPDATE users SET password_salt = ?, password_hash = ?,
                    is_active = 1, must_change_password = 1,
                    password_changed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (salt, password_hash, user["id"]),
            )
        return int(user["id"])

    def ensure_default_admin_credentials(self, username: str = "admin") -> bool:
        normalized_username = username.strip().casefold()
        if not normalized_username:
            raise ValueError("Tên đăng nhập quản trị không được để trống.")

        user = self.connection.execute(
            """
            SELECT id, password_salt, password_hash, role, is_active
            FROM users
            WHERE username = ?
            """,
            (normalized_username,),
        ).fetchone()
        if user is None:
            return False
        if user["role"] != "ADMIN":
            return False
        if verify_password("admin", user["password_salt"], user["password_hash"]):
            return False
        self.reset_admin_password(normalized_username)
        return True

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        normalized_username = username.strip().casefold()
        user = self.connection.execute(
            """
            SELECT id, username, display_name, password_salt, password_hash,
                   role, is_active, must_change_password
            FROM users WHERE username = ?
            """,
            (normalized_username,),
        ).fetchone()
        if (
            user is None
            or not user["is_active"]
            or not verify_password(
                password, user["password_salt"], user["password_hash"]
            )
        ):
            return None
        return {
            "id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"],
            "role": user["role"],
            "must_change_password": bool(user["must_change_password"]),
        }

    def has_permission(self, user_id: int, permission: str) -> bool:
        row = self.connection.execute(
            "SELECT role, is_active FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return bool(
            row
            and row["is_active"]
            and permission in ROLE_PERMISSIONS.get(row["role"], frozenset())
        )

    def set_user_role(self, user_id: int, role: str) -> None:
        if role not in ROLE_PERMISSIONS:
            raise ValueError("Vai trò được chọn không hợp lệ.")
        with self.connection:
            current = self.connection.execute(
                "SELECT role, is_active FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if current is None:
                raise ValueError("Không tìm thấy tài khoản.")
            if current["is_active"] and current["role"] == "ADMIN" and role != "ADMIN":
                admins = self.connection.execute(
                    "SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND is_active = 1"
                ).fetchone()[0]
                if admins <= 1:
                    raise ValueError(
                        "Không thể đổi vai trò của quản trị viên đang hoạt động cuối cùng."
                    )
            updated = self.connection.execute(
                "UPDATE users SET role = ? WHERE id = ?", (role, user_id)
            )
            if updated.rowcount != 1:
                raise ValueError("Không tìm thấy tài khoản.")

    def set_user_active(self, user_id: int, active: bool) -> None:
        with self.connection:
            user = self.connection.execute(
                "SELECT role, is_active FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if user is None:
                raise ValueError("Không tìm thấy tài khoản.")
            if not active and user["role"] == "ADMIN":
                active_admins = self.connection.execute(
                    "SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND is_active = 1"
                ).fetchone()[0]
                if active_admins <= 1:
                    raise ValueError("Không thể khóa quản trị viên đang hoạt động cuối cùng.")
            self.connection.execute(
                "UPDATE users SET is_active = ? WHERE id = ?",
                (int(active), user_id),
            )

    def change_password(self, user_id: int, current: str, new: str) -> None:
        user = self.connection.execute(
            "SELECT password_salt, password_hash FROM users WHERE id = ? AND is_active = 1",
            (user_id,),
        ).fetchone()
        if user is None or not verify_password(
            current, user["password_salt"], user["password_hash"]
        ):
            raise ValueError("Mật khẩu hiện tại không chính xác.")
        salt, password_hash = hash_password(new)
        with self.connection:
            self.connection.execute(
                """
                UPDATE users SET password_salt = ?, password_hash = ?,
                    password_changed_at = CURRENT_TIMESTAMP,
                    must_change_password = 0
                WHERE id = ?
                """,
                (salt, password_hash, user_id),
            )
