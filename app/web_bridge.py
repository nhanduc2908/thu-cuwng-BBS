from __future__ import annotations

import base64
import binascii
import hashlib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import ipaddress
import json
import logging
import mimetypes
import os
from pathlib import Path
import re
import secrets
import tempfile
import threading
import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from app.database import Database
from app.modules.auth.constants import ROLE_PERMISSIONS
from app.modules.auth.security import hash_password, verify_password


LOGGER = logging.getLogger("pet_store.web")
SESSION_COOKIE = "petcare_admin_session"
SESSION_IDLE_SECONDS = 30 * 60
CUSTOMER_SESSION_COOKIE = "petcare_customer_session"
CUSTOMER_SESSION_IDLE_SECONDS = 30 * 60
MAX_RESPONSE_ROWS = 5000
MODULE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "module_01_platform": ("dashboard.view",),
    "module_02_accounts": ("users.manage",),
    "module_03_dashboard": ("dashboard.view",),
    "module_04_pets": ("animals.view",),
    "module_05_housing": ("store.view",),
    "module_06_suppliers": ("imports.view",),
    "module_07_imports": ("imports.view",),
    "module_08_health": ("health.view",),
    "module_09_care": ("care.view",),
    "module_10_customers": ("sales.view",),
    "module_11_reservations": ("sales.view",),
    "module_12_orders": ("sales.view",),
    "module_13_memberships": ("membership.view",),
    "module_14_services": ("services.view",),
    "module_15_inventory": ("inventory.view",),
    "module_16_reports": ("reports.view",),
    "module_17_alerts": ("notifications.view", "audit.view"),
}
MODULE_MANAGE_PERMISSIONS: dict[str, str] = {
    "module_02_accounts": "users.manage",
    "module_04_pets": "animals.manage",
    "module_05_housing": "store.manage",
    "module_06_suppliers": "imports.manage",
    "module_07_imports": "imports.manage",
    "module_08_health": "health.manage",
    "module_09_care": "care.manage",
    "module_10_customers": "sales.manage",
    "module_11_reservations": "sales.manage",
    "module_12_orders": "sales.manage",
    "module_13_memberships": "membership.manage",
    "module_14_services": "services.manage",
    "module_15_inventory": "inventory.manage",
}
MODULE_DATASET_IDS = frozenset(
    f"module_{number:02d}_{name}"
    for number, name in (
        (1, "platform"), (2, "accounts"), (3, "dashboard"), (4, "pets"),
        (5, "housing"), (6, "suppliers"), (7, "imports"), (8, "health"),
        (9, "care"), (10, "customers"), (11, "reservations"), (12, "orders"),
        (13, "memberships"), (14, "services"), (15, "inventory"), (16, "reports"),
        (17, "alerts"),
    )
)


class LocalAdminBridge:
    """Serve the HTML application and authenticated local data APIs."""

    def __init__(
        self,
        database_path: str | Path,
        html_root: str | Path,
        host: str = "127.0.0.1",
        port: int = 8767,
    ) -> None:
        self.database_path = Path(database_path)
        self.html_root = Path(html_root).resolve()
        self.host = host
        self.port = port
        self._thread: threading.Thread | None = None
        self._server: HTTPServer | None = None
        self._ready = threading.Event()
        self._startup_error: BaseException | None = None
        self._stop_requested = threading.Event()

    @property
    def base_url(self) -> str:
        if self._server is None:
            return f"http://{self.host}:{self.port}"
        actual_host, actual_port = self._server.server_address[:2]
        return f"http://{actual_host}:{actual_port}"

    def start(self, timeout: float = 10.0) -> str:
        if self._thread and self._thread.is_alive():
            return self.base_url
        self._ready.clear()
        self._stop_requested.clear()
        self._startup_error = None
        self._thread = threading.Thread(
            target=self._serve,
            name="PetCareLocalAdminBridge",
            daemon=True,
        )
        self._thread.start()
        if not self._ready.wait(timeout):
            raise TimeoutError("Local admin bridge did not start in time.")
        if self._startup_error:
            raise OSError("Local admin bridge failed to start.") from self._startup_error
        return self.base_url

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_requested.set()
        if self._thread is not None:
            self._thread.join(timeout)
        if self._thread and self._thread.is_alive():
            LOGGER.warning("Local admin bridge did not stop before timeout.")

    def _serve(self) -> None:
        database: Database | None = None
        server: HTTPServer | None = None
        try:
            database = Database(self.database_path)
            server = HTTPServer((self.host, self.port), self._handler_type(database))
            server.timeout = 0.25
            self._server = server
            self._ready.set()
            LOGGER.info(
                "Local admin workspace available at %s/admin_store_management.html",
                self.base_url,
            )
            while not self._stop_requested.is_set():
                server.handle_request()
        except BaseException as error:
            self._startup_error = error
            self._ready.set()
            LOGGER.exception("Local admin bridge stopped unexpectedly")
        finally:
            if server is not None:
                server.server_close()
            self._server = None
            if database is not None:
                database.close()

    def _handler_type(self, database: Database) -> type[BaseHTTPRequestHandler]:
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "PetCareLocal/1.0"
            sessions: dict[str, dict[str, Any]] = {}
            customer_sessions: dict[str, dict[str, Any]] = {}

            def log_message(self, format_string: str, *args: Any) -> None:
                LOGGER.info("%s - %s", self.address_string(), format_string % args)

            def _allowed_origin(self) -> str | None:
                origin = self.headers.get("Origin", "")
                if not origin:
                    return None
                parsed = urlsplit(origin)
                request_path = urlsplit(self.path).path
                if request_path.startswith("/api/"):
                    request_path = request_path[4:]
                if request_path == "/customer" or request_path.startswith("/customer/"):
                    expected_origin = f"http://{self.headers.get('Host', '').lower()}"
                    return origin if (
                        parsed.scheme == "http"
                        and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
                        and origin.lower() == expected_origin
                    ) else None
                active_port = (
                    bridge._server.server_address[1]
                    if bridge._server is not None
                    else bridge.port
                )
                return origin if (
                    parsed.scheme == "http"
                    and parsed.hostname in {"localhost", "127.0.0.1"}
                    and parsed.port in {8765, 8766, 8767, bridge.port, active_port}
                ) else None

            def end_headers(self) -> None:
                origin = self._allowed_origin()
                if origin:
                    self.send_header("Access-Control-Allow-Origin", origin)
                    self.send_header("Access-Control-Allow-Credentials", "true")
                    self.send_header("Vary", "Origin")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "same-origin")
                super().end_headers()

            def _json(
                self,
                status: HTTPStatus,
                payload: dict[str, Any],
                extra_headers: dict[str, str] | None = None,
            ) -> None:
                content = json.dumps(
                    payload, ensure_ascii=False, default=str
                ).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(content)))
                for key, value in (extra_headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(content)

            def _body(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 12 * 1024 * 1024:
                    raise ValueError("Request body is missing or too large.")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("JSON object expected.")
                return payload

            def _normalized_path(self) -> str:
                parsed = urlsplit(self.path)
                request_path = parsed.path
                if request_path.startswith("/api"):
                    request_path = request_path[4:] or "/"
                return request_path

            def _require_same_site_post(self) -> bool:
                if self._allowed_origin() is None or self.headers.get(
                    "X-PetCare-Request"
                ) != "1":
                    self._json(
                        HTTPStatus.FORBIDDEN,
                        {"error": "Request origin rejected."},
                    )
                    return False
                return True

            def _cookie_token(self) -> str:
                for part in self.headers.get("Cookie", "").split(";"):
                    key, separator, value = part.strip().partition("=")
                    if separator and key == SESSION_COOKIE:
                        return value
                return ""

            def _session(self) -> dict[str, Any] | None:
                token = self._cookie_token()
                session = self.sessions.get(token)
                if not session:
                    return None
                if time.monotonic() - session["last_seen"] > SESSION_IDLE_SECONDS:
                    self.sessions.pop(token, None)
                    return None
                user = database.connection.execute(
                    "SELECT username, display_name, role, is_active, must_change_password "
                    "FROM users WHERE id = ?",
                    (session["user_id"],),
                ).fetchone()
                if user is None or not user["is_active"]:
                    self.sessions.pop(token, None)
                    return None
                session.update(
                    username=user["username"],
                    display_name=user["display_name"],
                    role=user["role"],
                    must_change_password=bool(user["must_change_password"]),
                    last_seen=time.monotonic(),
                )
                return session

            def _customer_portal_enabled(self) -> bool:
                if bridge._server is None:
                    return False
                bound_host = str(bridge._server.server_address[0]).split("%", 1)[0]
                try:
                    return ipaddress.ip_address(bound_host).is_loopback
                except ValueError:
                    return False

            def _customer_session_token(self) -> str:
                for part in self.headers.get("Cookie", "").split(";"):
                    key, separator, value = part.strip().partition("=")
                    if separator and key == CUSTOMER_SESSION_COOKIE:
                        return value
                return ""

            def _customer_session(self) -> dict[str, Any] | None:
                token = self._customer_session_token()
                session = self.customer_sessions.get(token)
                if not session:
                    return None
                if time.monotonic() - session["last_seen"] > CUSTOMER_SESSION_IDLE_SECONDS:
                    self.customer_sessions.pop(token, None)
                    return None
                account = database.connection.execute(
                    """
                    SELECT id, username, display_name, customer_id
                    FROM customer_portal_accounts
                    WHERE id = ? AND status = 'ACTIVE' AND customer_id IS NOT NULL
                    """,
                    (session["account_id"],),
                ).fetchone()
                if account is None:
                    self.customer_sessions.pop(token, None)
                    return None
                session.update(
                    username=account["username"],
                    display_name=account["display_name"],
                    customer_id=int(account["customer_id"]),
                    last_seen=time.monotonic(),
                )
                return session

            def _customer_portal_staff_session(self) -> dict[str, Any] | None:
                staff = self._session()
                if staff is None:
                    self._json(HTTPStatus.UNAUTHORIZED, {"error": "Staff sign-in required."})
                    return None
                staff_id = int(staff["user_id"])
                if not database.has_permission(staff_id, "sales.manage"):
                    self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                    return None
                database.set_actor(staff_id)
                return staff

            @staticmethod
            def _portal_cookie(token: str, max_age: int) -> str:
                return (
                    f"{CUSTOMER_SESSION_COOKIE}={token}; HttpOnly; SameSite=Strict; "
                    f"Path=/; Max-Age={max_age}"
                )

            def _customer_portal_records(self, customer_id: int) -> dict[str, Any]:
                customer = database.connection.execute(
                    """
                    SELECT customer_code, name, phone, email, address, created_at
                    FROM customers WHERE id = ?
                    """,
                    (customer_id,),
                ).fetchone()
                if customer is None:
                    raise LookupError("Linked customer record is unavailable.")
                pets = database.connection.execute(
                    """
                    SELECT id, name, species, breed_name, birth_date, sex, color,
                           weight_kg, health_status, created_at
                    FROM pet_profiles WHERE customer_id = ?
                    ORDER BY created_at DESC, id DESC
                    """,
                    (customer_id,),
                ).fetchall()
                appointments = database.connection.execute(
                    """
                    SELECT sa.appointment_code, sa.pet_name, sa.species,
                           sa.scheduled_at, sa.duration_minutes, sa.total_price,
                           sa.status, sp.name AS service_name
                    FROM service_appointments sa
                    LEFT JOIN service_packages sp ON sp.id = sa.package_id
                    WHERE sa.customer_id = ?
                    ORDER BY sa.scheduled_at DESC, sa.id DESC
                    """,
                    (customer_id,),
                ).fetchall()
                orders = database.connection.execute(
                    """
                    SELECT order_code, ordered_at, status, total_amount, paid_at
                    FROM sales_orders WHERE customer_id = ?
                    ORDER BY ordered_at DESC, id DESC
                    """,
                    (customer_id,),
                ).fetchall()
                reservations = database.connection.execute(
                    """
                    SELECT r.reserved_at, r.expires_at, r.deposit, r.status,
                           a.name AS animal_name, a.species AS animal_species
                    FROM reservations r
                    JOIN animals a ON a.id = r.animal_id
                    WHERE r.customer_id = ?
                    ORDER BY r.reserved_at DESC, r.id DESC
                    """,
                    (customer_id,),
                ).fetchall()
                memberships = database.connection.execute(
                    """
                    SELECT m.membership_code, m.start_date, m.end_date, m.status,
                           mp.name AS plan_name
                    FROM memberships m
                    JOIN membership_plans mp ON mp.id = m.plan_id
                    WHERE m.customer_id = ?
                    ORDER BY m.end_date DESC, m.id DESC
                    """,
                    (customer_id,),
                ).fetchall()
                return {
                    "source": "local_database",
                    "customer": dict(customer),
                    "pets": self._plain_records(pets),
                    "appointments": self._plain_records(appointments),
                    "orders": self._plain_records(orders),
                    "reservations": self._plain_records(reservations),
                    "memberships": self._plain_records(memberships),
                }

            def _customer_request(self, method: str) -> bool:
                request_path = self._normalized_path()
                if request_path != "/customer" and not request_path.startswith("/customer/"):
                    return False
                if not self._customer_portal_enabled():
                    self._json(
                        HTTPStatus.FORBIDDEN,
                        {"error": "Customer portal is available only on a loopback-bound bridge."},
                    )
                    return True

                if method == "GET" and request_path in {
                    "/customer/accounts",
                    "/customer/invites",
                }:
                    if self._customer_portal_staff_session() is None:
                        return True
                    parameters = parse_qs(urlsplit(self.path).query)
                    status_filter = parameters.get("status", ["PENDING"])[0].upper()
                    try:
                        if request_path == "/customer/accounts":
                            records = database.list_customer_portal_accounts(status_filter)
                        else:
                            records = database.list_customer_portal_invites(
                                parameters.get("status", ["ALL"])[0].upper()
                            )
                        self._json(
                            HTTPStatus.OK,
                            {"records": self._plain_records(records), "total": len(records)},
                        )
                    except (PermissionError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    return True

                if method == "GET" and request_path == "/customer/session":
                    session = self._customer_session()
                    if session is None:
                        self._json(HTTPStatus.UNAUTHORIZED, {"authenticated": False})
                    else:
                        self._json(
                            HTTPStatus.OK,
                            {
                                "authenticated": True,
                                "user": {
                                    "username": session["username"],
                                    "display_name": session["display_name"],
                                },
                            },
                        )
                    return True

                if method == "GET" and request_path == "/customer/portal":
                    session = self._customer_session()
                    if session is None:
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Customer sign-in required."})
                        return True
                    try:
                        self._json(
                            HTTPStatus.OK,
                            self._customer_portal_records(int(session["customer_id"])),
                        )
                    except LookupError as error:
                        self._json(HTTPStatus.FORBIDDEN, {"error": str(error)})
                    except Exception:
                        LOGGER.exception("Could not read customer portal records")
                        self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not read customer records."})
                    return True

                if method == "POST" and request_path == "/customer/register":
                    try:
                        body = self._body()
                        username = str(body.get("username", "")).strip()
                        display_name = str(body.get("display_name", "")).strip()
                        password = str(body.get("password", ""))
                        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
                            raise ValueError("Username must be 3–50 letters, numbers, dots, underscores, or hyphens.")
                        if not display_name or len(display_name) > 120:
                            raise ValueError("A display name of at most 120 characters is required.")
                        salt, password_hash = hash_password(password)
                        with database.connection:
                            database.connection.execute(
                                """
                                INSERT INTO customer_portal_accounts
                                    (username, display_name, password_salt, password_hash, status)
                                VALUES (?, ?, ?, ?, 'PENDING')
                                """,
                                (username, display_name, salt, password_hash),
                            )
                        self._json(
                            HTTPStatus.ACCEPTED,
                            {"registered": True, "status": "PENDING", "message": "Registration submitted for staff approval."},
                        )
                    except ValueError as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    except Exception as error:
                        if "UNIQUE constraint failed" in str(error):
                            self._json(HTTPStatus.CONFLICT, {"error": "That username is already registered."})
                        else:
                            LOGGER.exception("Could not register customer portal account")
                            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not submit registration."})
                    return True

                if method == "POST" and request_path == "/customer/accept-invite":
                    try:
                        body = self._body()
                        invite_code = str(body.get("invite_code", "")).strip()
                        username = str(body.get("username", "")).strip()
                        display_name = str(body.get("display_name", "")).strip()
                        password = str(body.get("password", ""))
                        if len(invite_code) > 256 or not invite_code:
                            raise ValueError("A valid invitation code is required.")
                        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
                            raise ValueError("Username must be 3–50 letters, numbers, dots, underscores, or hyphens.")
                        if not display_name or len(display_name) > 120:
                            raise ValueError("A display name of at most 120 characters is required.")
                        salt, password_hash = hash_password(password)
                        token_hash = hashlib.sha256(invite_code.encode("utf-8")).hexdigest()
                        with database.connection:
                            invite = database.connection.execute(
                                """
                                SELECT id, customer_id FROM customer_portal_invites
                                WHERE token_hash = ? AND redeemed_at IS NULL
                                  AND expires_at > CURRENT_TIMESTAMP
                                """,
                                (token_hash,),
                            ).fetchone()
                            if invite is None:
                                self._json(HTTPStatus.BAD_REQUEST, {"error": "Invitation is invalid, expired, or already used."})
                                return True
                            cursor = database.connection.execute(
                                """
                                INSERT INTO customer_portal_accounts
                                    (username, display_name, password_salt, password_hash,
                                     status, customer_id, approved_at)
                                VALUES (?, ?, ?, ?, 'ACTIVE', ?, CURRENT_TIMESTAMP)
                                """,
                                (username, display_name, salt, password_hash, int(invite["customer_id"])),
                            )
                            changed = database.connection.execute(
                                """
                                UPDATE customer_portal_invites SET redeemed_at = CURRENT_TIMESTAMP
                                WHERE id = ? AND redeemed_at IS NULL
                                """,
                                (int(invite["id"]),),
                            ).rowcount
                            if changed != 1:
                                raise ValueError("Invitation has already been used.")
                            account_id = int(cursor.lastrowid)
                        token = secrets.token_urlsafe(32)
                        self.customer_sessions[token] = {
                            "account_id": account_id,
                            "last_seen": time.monotonic(),
                        }
                        self._json(
                            HTTPStatus.CREATED,
                            {"authenticated": True},
                            {"Set-Cookie": self._portal_cookie(token, CUSTOMER_SESSION_IDLE_SECONDS)},
                        )
                    except ValueError as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    except Exception as error:
                        if "UNIQUE constraint failed" in str(error):
                            self._json(HTTPStatus.CONFLICT, {"error": "Username already exists or customer already has a portal account."})
                        else:
                            LOGGER.exception("Could not accept customer portal invitation")
                            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not accept invitation."})
                    return True

                if method == "POST" and request_path == "/customer/login":
                    try:
                        body = self._body()
                        username = str(body.get("username", "")).strip()
                        password = str(body.get("password", ""))
                        account = database.connection.execute(
                            """
                            SELECT id, password_salt, password_hash, status
                            FROM customer_portal_accounts WHERE username = ?
                            """,
                            (username,),
                        ).fetchone()
                        if account is None or not verify_password(
                            password, account["password_salt"], account["password_hash"]
                        ):
                            self._json(HTTPStatus.UNAUTHORIZED, {"error": "Username or password is incorrect."})
                            return True
                        if account["status"] == "PENDING":
                            self._json(
                                HTTPStatus.FORBIDDEN,
                                {"error": "This account is pending staff approval.", "pendingApproval": True},
                            )
                            return True
                        if account["status"] != "ACTIVE":
                            self._json(HTTPStatus.UNAUTHORIZED, {"error": "This account is unavailable."})
                            return True
                        token = secrets.token_urlsafe(32)
                        self.customer_sessions[token] = {
                            "account_id": int(account["id"]),
                            "last_seen": time.monotonic(),
                        }
                        self._json(
                            HTTPStatus.OK,
                            {"authenticated": True},
                            {"Set-Cookie": self._portal_cookie(token, CUSTOMER_SESSION_IDLE_SECONDS)},
                        )
                    except (ValueError, json.JSONDecodeError):
                        self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid customer login request."})
                    return True

                if method == "POST" and request_path == "/customer/logout":
                    token = self._customer_session_token()
                    self.customer_sessions.pop(token, None)
                    self._json(
                        HTTPStatus.OK,
                        {"authenticated": False},
                        {"Set-Cookie": self._portal_cookie("", 0)},
                    )
                    return True

                if method == "POST" and request_path == "/customer/invites":
                    staff = self._customer_portal_staff_session()
                    if staff is None:
                        return True
                    try:
                        body = self._body()
                        customer_id = int(body.get("customer_id", 0))
                        invite = database.create_customer_portal_invite(customer_id)
                        self._json(HTTPStatus.CREATED, invite)
                    except (PermissionError, TypeError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    return True

                approval = re.fullmatch(r"/customer/accounts/(\d+)/approve", request_path)
                if method == "POST" and approval:
                    if self._customer_portal_staff_session() is None:
                        return True
                    try:
                        body = self._body()
                        account_id = int(approval.group(1))
                        customer_id = int(body.get("customer_id", 0))
                        if not database.approve_customer_portal_account(account_id, customer_id):
                            raise ValueError("Pending account or available customer link not found.")
                        self._json(HTTPStatus.OK, {"approved": True})
                    except (PermissionError, TypeError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    except Exception as error:
                        if "UNIQUE constraint failed" in str(error):
                            self._json(HTTPStatus.CONFLICT, {"error": "Customer already has a portal account."})
                        else:
                            LOGGER.exception("Could not approve customer portal account")
                            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not approve account."})
                    return True

                rejection = re.fullmatch(r"/customer/accounts/(\d+)/reject", request_path)
                if method == "POST" and rejection:
                    if self._customer_portal_staff_session() is None:
                        return True
                    try:
                        account_id = int(rejection.group(1))
                        if not database.reject_customer_portal_account(account_id):
                            raise ValueError("Pending account not found.")
                        self._json(HTTPStatus.OK, {"rejected": True})
                    except (PermissionError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    return True

                expiry = re.fullmatch(r"/customer/invites/(\d+)/expire", request_path)
                if method == "POST" and expiry:
                    if self._customer_portal_staff_session() is None:
                        return True
                    try:
                        invite_id = int(expiry.group(1))
                        if not database.expire_customer_portal_invite(invite_id):
                            raise ValueError("Active invitation not found.")
                        self._json(HTTPStatus.OK, {"expired": True})
                    except (PermissionError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    return True

                self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown customer portal endpoint."})
                return True

            @staticmethod
            def _plain_records(rows: Any) -> list[dict[str, Any]]:
                result = []
                for row in rows:
                    item = dict(row) if not isinstance(row, dict) else dict(row)
                    for key, value in tuple(item.items()):
                        if isinstance(value, bytes):
                            item[key] = f"[{len(value)} bytes]"
                    result.append(item)
                return result

            def _module_records(
                self, module_id: str, session: dict[str, Any]
            ) -> list[dict[str, Any]]:
                user_id = int(session["user_id"])
                database.set_actor(user_id)
                if module_id == "module_01_platform":
                    counts = database.dashboard.dashboard_counts()
                    return [{"databasePath": str(database.path), "sqliteVersion": database.connection.execute("SELECT sqlite_version()").fetchone()[0]}] + [
                        {"animalStatus": status, "count": count}
                        for status, count in counts.items()
                    ]
                if module_id == "module_02_accounts":
                    return self._plain_records(database.list_users())
                if module_id == "module_03_dashboard":
                    counts = database.dashboard.dashboard_counts()
                    return [{"metric": key, "value": value} for key, value in counts.items()] + self._plain_records(database.recent_animals(20))
                if module_id == "module_04_pets":
                    return self._plain_records(database.list_animals())
                if module_id == "module_05_housing":
                    return self._plain_records(database.list_cages())
                if module_id == "module_06_suppliers":
                    return self._plain_records(database.list_suppliers())
                if module_id == "module_07_imports":
                    return self._plain_records(database.list_import_batches())
                if module_id == "module_08_health":
                    return self._plain_records(database.list_health_records())
                if module_id == "module_09_care":
                    return self._plain_records(database.list_care_tasks())
                if module_id == "module_10_customers":
                    return self._plain_records(database.list_customers())
                if module_id == "module_11_reservations":
                    return self._plain_records(database.list_reservations())
                if module_id == "module_12_orders":
                    return self._plain_records(database.list_sales_orders())
                if module_id == "module_13_memberships":
                    return self._plain_records(database.list_memberships())
                if module_id == "module_14_services":
                    return self._plain_records(database.list_service_appointments())
                if module_id == "module_15_inventory":
                    return self._plain_records(database.list_inventory_items())
                if module_id == "module_16_reports":
                    return self._plain_records(database.report_inventory())
                if module_id == "module_17_alerts":
                    records: list[dict[str, Any]] = []
                    if database.has_permission(user_id, "notifications.view"):
                        records.extend(database.list_operational_alerts())
                    if database.has_permission(user_id, "audit.view"):
                        records.extend(self._plain_records(database.list_audit_events(limit=200)))
                    return records
                raise KeyError(module_id)

            @staticmethod
            def _dataset_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
                rows = payload.get("demoData")
                if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                    raise ValueError("Dataset must contain an array of demoData objects.")
                return rows

            def _dataset_file(self, module_id: str) -> Path:
                if module_id not in MODULE_DATASET_IDS:
                    raise ValueError("Unknown prepared dataset.")
                target = (bridge.html_root / "data" / f"{module_id}.json").resolve()
                if not target.is_relative_to(bridge.html_root) or not target.is_file():
                    raise FileNotFoundError("Prepared dataset file is unavailable.")
                return target

            def _read_dataset_file(self, module_id: str) -> tuple[Path, dict[str, Any]]:
                target = self._dataset_file(module_id)
                with target.open("r", encoding="utf-8") as dataset_file:
                    payload = json.load(dataset_file)
                if not isinstance(payload, dict):
                    raise ValueError("Prepared dataset must be a JSON object.")
                self._dataset_rows(payload)
                return target, payload

            def _write_dataset_file(
                self, module_id: str, target: Path, payload: dict[str, Any]
            ) -> None:
                content = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
                if len(content) > 12 * 1024 * 1024:
                    raise ValueError("Updated dataset exceeds the 12 MB limit.")
                backup_root = bridge.database_path.parent / "dataset_backups"
                backup_root.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup = backup_root / f"{module_id}-{timestamp}-{secrets.token_hex(4)}.json"
                temporary_path: Path | None = None
                try:
                    with target.open("rb") as source, backup.open("xb") as destination:
                        destination.write(source.read())
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        dir=target.parent,
                        prefix=f".{module_id}-",
                        suffix=".tmp",
                        delete=False,
                    ) as temporary:
                        temporary.write(content)
                        temporary.flush()
                        os.fsync(temporary.fileno())
                        temporary_path = Path(temporary.name)
                    os.replace(temporary_path, target)
                except Exception:
                    if temporary_path is not None:
                        temporary_path.unlink(missing_ok=True)
                    backup.unlink(missing_ok=True)
                    raise

            def _dataset_records(self, module_id: str, source: str) -> list[dict[str, Any]]:
                if source == "live":
                    return [
                        {"id": index, "record": record, "archived": False}
                        for index, record in enumerate(
                            self._plain_records(self._module_records(module_id, self._session()))
                        )
                    ]
                if source == "file":
                    _, payload = self._read_dataset_file(module_id)
                    return [
                        {"id": index, "record": record, "archived": bool(record.get("_archived"))}
                        for index, record in enumerate(self._dataset_rows(payload))
                    ]
                if source == "sqlite":
                    return [
                        {
                            "id": row["id"],
                            "record": json.loads(row["record_json"]),
                            "archived": bool(row["is_archived"]),
                            "sourceKey": row["source_key"],
                            "updatedAt": row["updated_at"],
                        }
                        for row in database.list_web_dataset_records(module_id)
                    ]
                raise ValueError("source must be 'file' or 'sqlite'.")

            def _dataset_authorized(
                self, module_id: str, session: dict[str, Any], write: bool = False
            ) -> bool:
                if module_id not in MODULE_DATASET_IDS:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown module."})
                    return False
                user_id = int(session["user_id"])
                permissions = (
                    (MODULE_MANAGE_PERMISSIONS.get(module_id),)
                    if write
                    else MODULE_PERMISSIONS.get(module_id)
                )
                if not permissions or not any(
                    database.has_permission(user_id, permission)
                    for permission in permissions
                    if permission
                ):
                    self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                    return False
                return True

            def _dataset_request(self, method: str) -> bool:
                request_path = self._normalized_path()
                match = re.fullmatch(
                    r"/datasets/(module_[0-9]{2}_[a-z]+)/records(?:/([0-9]+))?",
                    request_path,
                )
                import_match = re.fullmatch(
                    r"/datasets/(module_[0-9]{2}_[a-z]+)/import",
                    request_path,
                )
                if not match and not import_match:
                    return False
                session = self._session()
                if not session:
                    self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                    return True
                route = match or import_match
                module_id = route.group(1)
                is_write = method in {"POST", "PUT", "DELETE"}
                if not self._dataset_authorized(module_id, session, is_write):
                    return True
                user_id = int(session["user_id"])
                database.set_actor(user_id)
                parameters = parse_qs(urlsplit(self.path).query)
                source = parameters.get("source", ["file"])[0]
                record_id = int(match.group(2)) if match and match.group(2) else None

                try:
                    if method == "GET" and match:
                        records = self._dataset_records(module_id, source)
                        self._json(HTTPStatus.OK, {
                            "moduleId": module_id,
                            "source": source,
                            "readOnly": (
                                source == "live"
                                or module_id not in MODULE_MANAGE_PERMISSIONS
                            ),
                            "canManage": (
                                source != "live"
                                and
                                module_id in MODULE_MANAGE_PERMISSIONS
                                and database.has_permission(
                                    user_id, MODULE_MANAGE_PERMISSIONS[module_id]
                                )
                            ),
                            "records": records,
                            "total": len(records),
                        })
                        return True

                    body = self._body() if method in {"POST", "PUT"} else {}
                    if method == "POST" and import_match:
                        if source != "sqlite":
                            raise ValueError("JSON import requires source=sqlite.")
                        _, payload = self._read_dataset_file(module_id)
                        active_rows = [
                            row for row in self._dataset_rows(payload)
                            if not row.get("_archived")
                        ]
                        inserted, skipped = database.import_web_dataset_records(
                            module_id, active_rows, user_id
                        )
                        database.record_audit(
                            user_id, "IMPORT_PREPARED_DATA", "web_dataset",
                            details=f"{module_id}; inserted={inserted}; skipped={skipped}",
                        )
                        self._json(HTTPStatus.OK, {
                            "inserted": inserted,
                            "skipped": skipped,
                            "message": "Dataset imported into the SQLite workspace.",
                        })
                        return True

                    if method == "POST" and match:
                        record = body.get("record")
                        if not isinstance(record, dict):
                            raise ValueError("A JSON record object is required.")
                        if source == "file":
                            target, payload = self._read_dataset_file(module_id)
                            rows = self._dataset_rows(payload)
                            rows.append({**record, "_webRecordId": secrets.token_urlsafe(12)})
                            self._write_dataset_file(module_id, target, payload)
                            created_id = len(rows) - 1
                        elif source == "sqlite":
                            created_id = database.create_web_dataset_record(
                                module_id, secrets.token_urlsafe(12), record, user_id
                            )
                        else:
                            raise ValueError("source must be 'file' or 'sqlite'.")
                        database.record_audit(
                            user_id, "CREATE", "web_dataset_record", created_id, module_id
                        )
                        self._json(HTTPStatus.CREATED, {"id": created_id, "message": "Record created."})
                        return True

                    if method == "PUT" and match and record_id is not None:
                        record = body.get("record")
                        if not isinstance(record, dict):
                            raise ValueError("A JSON record object is required.")
                        if source == "file":
                            target, payload = self._read_dataset_file(module_id)
                            rows = self._dataset_rows(payload)
                            if record_id < 0 or record_id >= len(rows) or rows[record_id].get("_archived"):
                                raise ValueError("Record does not exist or is archived.")
                            rows[record_id] = {
                                **record,
                                "_webRecordId": rows[record_id].get(
                                    "_webRecordId", secrets.token_urlsafe(12)
                                ),
                            }
                            self._write_dataset_file(module_id, target, payload)
                        elif source == "sqlite":
                            database.update_web_dataset_record(module_id, record_id, record)
                        else:
                            raise ValueError("source must be 'file' or 'sqlite'.")
                        database.record_audit(
                            user_id, "UPDATE", "web_dataset_record", record_id, module_id
                        )
                        self._json(HTTPStatus.OK, {"id": record_id, "message": "Record updated."})
                        return True

                    if method == "DELETE" and match and record_id is not None:
                        if source == "file":
                            target, payload = self._read_dataset_file(module_id)
                            rows = self._dataset_rows(payload)
                            if record_id < 0 or record_id >= len(rows) or rows[record_id].get("_archived"):
                                raise ValueError("Record does not exist or is already archived.")
                            rows[record_id]["_archived"] = True
                            self._write_dataset_file(module_id, target, payload)
                        elif source == "sqlite":
                            database.archive_web_dataset_record(module_id, record_id, user_id)
                        else:
                            raise ValueError("source must be 'file' or 'sqlite'.")
                        database.record_audit(
                            user_id, "ARCHIVE", "web_dataset_record", record_id, module_id
                        )
                        self._json(HTTPStatus.OK, {"id": record_id, "message": "Record archived."})
                        return True

                    self._json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Unsupported dataset operation."})
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                except FileNotFoundError as error:
                    self._json(HTTPStatus.NOT_FOUND, {"error": str(error)})
                except Exception:
                    LOGGER.exception("Could not process dataset operation for %s", module_id)
                    self._json(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": "Could not process dataset operation."},
                    )
                return True

            def do_OPTIONS(self) -> None:
                if self._allowed_origin() is None:
                    self._json(HTTPStatus.FORBIDDEN, {"error": "Request origin rejected."})
                    return
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-PetCare-Request")
                self.send_header("Access-Control-Max-Age", "600")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                request_path = self._normalized_path()

                if self._customer_request("GET"):
                    return

                if request_path == "/session":
                    session = self._session()
                    if not session:
                        self._json(HTTPStatus.UNAUTHORIZED, {"authenticated": False})
                        return
                    self._json(HTTPStatus.OK, {
                        "authenticated": True,
                        "user": {
                            key: session[key]
                            for key in ("user_id", "username", "display_name", "role")
                        },
                        "permissions": sorted(ROLE_PERMISSIONS.get(session["role"], ())),
                        "must_change_password": bool(session.get("must_change_password", False)),
                    })
                    return

                if self._dataset_request("GET"):
                    return

                record_match = re.fullmatch(
                    r"/modules/([a-z0-9_]+)/records", request_path
                )
                if record_match:
                    session = self._session()
                    if not session:
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                        return
                    module_id = record_match.group(1)
                    required = MODULE_PERMISSIONS.get(module_id)
                    user_id = int(session["user_id"])
                    if required is None:
                        self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown module."})
                        return
                    if not any(database.has_permission(user_id, permission) for permission in required):
                        self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                        return
                    try:
                        records = self._module_records(module_id, session)
                    except PermissionError:
                        self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                        return
                    except Exception:
                        LOGGER.exception("Could not read module %s", module_id)
                        self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not read module data."})
                        return
                    parameters = parse_qs(parsed.query)
                    search = parameters.get("q", [""])[0].strip().casefold()
                    if search:
                        records = [record for record in records if search in json.dumps(record, ensure_ascii=False, default=str).casefold()]
                    total = len(records)
                    truncated = total > MAX_RESPONSE_ROWS
                    records = records[:MAX_RESPONSE_ROWS]
                    self._json(HTTPStatus.OK, {
                        "moduleId": module_id,
                        "source": "sqlite",
                        "readOnly": True,
                        "total": total,
                        "records": records,
                        "truncated": truncated,
                    })
                    return

                batch_match = re.fullmatch(r"/imports/(\d+)/animals", request_path)
                if batch_match:
                    session = self._session()
                    if not session:
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                        return
                    user_id = int(session["user_id"])
                    if not database.has_permission(user_id, "imports.view"):
                        self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                        return
                    database.set_actor(user_id)
                    rows = self._plain_records(database.list_import_animals(int(batch_match.group(1))))
                    self._json(HTTPStatus.OK, {"source": "sqlite", "records": rows, "total": len(rows)})
                    return

                photo_match = re.fullmatch(r"/intake-receipts/(\d+)/photo", request_path)
                if photo_match:
                    session = self._session()
                    if not session:
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                        return
                    user_id = int(session["user_id"])
                    if not any(database.has_permission(user_id, permission) for permission in ("imports.view", "animals.view")):
                        self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                        return
                    database.set_actor(user_id)
                    receipt = database.get_intake_receipt(int(photo_match.group(1)))
                    if receipt is None:
                        self._json(HTTPStatus.NOT_FOUND, {"error": "No intake attachment for this record."})
                        return
                    database.record_audit(user_id, "VIEW_INTAKE_ATTACHMENT", "animal", int(photo_match.group(1)))
                    photo = receipt["photo_data"]
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", receipt["photo_mime"])
                    self.send_header("Content-Length", str(len(photo)))
                    self.send_header("Cache-Control", "private, no-store")
                    self.send_header("Content-Disposition", "inline; filename=intake-receipt")
                    self.end_headers()
                    self.wfile.write(photo)
                    return

                self._serve_static(request_path)

            def _serve_static(self, request_path: str) -> None:
                relative = unquote(request_path).lstrip("/") or "index.html"
                target = (bridge.html_root / relative).resolve()
                if not target.is_relative_to(bridge.html_root) or not target.is_file():
                    self._json(HTTPStatus.NOT_FOUND, {"error": "File not found."})
                    return
                content = target.read_bytes()
                content_type = {
                    ".html": "text/html; charset=utf-8",
                    ".css": "text/css; charset=utf-8",
                    ".js": "text/javascript; charset=utf-8",
                    ".json": "application/json; charset=utf-8",
                    ".svg": "image/svg+xml",
                }.get(target.suffix.lower())
                if content_type is None:
                    content_type = mimetypes.guess_type(target.name)[0]
                if content_type is None:
                    content_type = "application/octet-stream"
                elif content_type.startswith("text/") or content_type in {
                    "application/javascript",
                    "application/json",
                    "image/svg+xml",
                }:
                    content_type = f"{content_type}; charset=utf-8"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

            def do_POST(self) -> None:
                if self._allowed_origin() is None or self.headers.get("X-PetCare-Request") != "1":
                    self._json(HTTPStatus.FORBIDDEN, {"error": "Request origin rejected."})
                    return
                request_path = self._normalized_path()
                if self._customer_request("POST"):
                    return
                if self._dataset_request("POST"):
                    return
                if request_path == "/login":
                    try:
                        body = self._body()
                        username = str(body.get("username", "")).strip()
                        user = database.authenticate(username, str(body.get("password", "")))
                    except (ValueError, json.JSONDecodeError):
                        self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid login request."})
                        return
                    if user is None:
                        database.record_audit(None, "LOGIN_FAILED", "user", details=f"web username={username[:64]}")
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã khóa."})
                        return
                    token = secrets.token_urlsafe(32)
                    self.sessions[token] = {
                        "user_id": int(user["id"]),
                        "username": user["username"],
                        "display_name": user["display_name"],
                        "role": user["role"],
                        "must_change_password": bool(user["must_change_password"]),
                        "last_seen": time.monotonic(),
                    }
                    database.set_actor(int(user["id"]))
                    database.record_audit(int(user["id"]), "WEB_LOGIN", "user", int(user["id"]))
                    self._json(
                        HTTPStatus.OK,
                        {
                            "authenticated": True,
                            "must_change_password": bool(user["must_change_password"]),
                        },
                        {
                            "Set-Cookie": f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_IDLE_SECONDS}"
                        },
                    )
                    return

                if request_path == "/logout":
                    token = self._cookie_token()
                    self.sessions.pop(token, None)
                    self._json(HTTPStatus.OK, {"authenticated": False}, {
                        "Set-Cookie": f"{SESSION_COOKIE}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"
                    })
                    return

                create_batch = request_path == "/imports/batches"
                add_animal = re.fullmatch(r"/imports/batches/(\d+)/animals", request_path)
                if create_batch or add_animal:
                    session = self._session()
                    if not session:
                        self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                        return
                    user_id = int(session["user_id"])
                    if not database.has_permission(user_id, "imports.manage"):
                        self._json(HTTPStatus.FORBIDDEN, {"error": "Insufficient permission."})
                        return
                    database.set_actor(user_id)
                    try:
                        body = self._body()
                        if create_batch:
                            batch_id = database.create_import_batch(body)
                            self._json(HTTPStatus.CREATED, {"id": batch_id, "message": "Import voucher created."})
                            return
                        encoded_photo = str(body.pop("photoBase64", ""))
                        if len(encoded_photo) > 11 * 1024 * 1024:
                            raise ValueError("Ảnh chứng từ vượt quá giới hạn 8 MB.")
                        try:
                            photo_data = base64.b64decode(encoded_photo, validate=True)
                        except (ValueError, binascii.Error) as error:
                            raise ValueError("Ảnh chứng từ không đúng định dạng Base64.") from error
                        body["photo_data"] = photo_data
                        body["photo_mime"] = str(body.pop("photoMime", ""))
                        animal_id = database.add_import_animal(int(add_animal.group(1)), body)
                        self._json(HTTPStatus.CREATED, {"animalId": animal_id, "message": "Animal and intake attachment saved."})
                    except (KeyError, TypeError, ValueError) as error:
                        self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                    except Exception:
                        LOGGER.exception("Could not save import/intake record")
                        self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not save record."})
                    return

                self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})

            def do_PUT(self) -> None:
                if not self._require_same_site_post():
                    return
                if self._customer_request("PUT"):
                    return
                if self._dataset_request("PUT"):
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})

            def do_DELETE(self) -> None:
                if not self._require_same_site_post():
                    return
                if self._customer_request("DELETE"):
                    return
                if self._dataset_request("DELETE"):
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})

        return Handler