from __future__ import annotations

import base64
import binascii
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from pathlib import Path
import re
import secrets
import threading
import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from app.database import Database
from app.modules.auth.constants import ROLE_PERMISSIONS


LOGGER = logging.getLogger("pet_store.web")
SESSION_COOKIE = "petcare_admin_session"
SESSION_IDLE_SECONDS = 30 * 60
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


class LocalAdminBridge:
    """Serve the admin HTML and authenticated, read-only SQLite APIs locally."""

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

            def log_message(self, format_string: str, *args: Any) -> None:
                LOGGER.info("%s - %s", self.address_string(), format_string % args)

            def _allowed_origin(self) -> str | None:
                origin = self.headers.get("Origin", "")
                if not origin:
                    return None
                parsed = urlsplit(origin)
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

            def do_OPTIONS(self) -> None:
                if self._allowed_origin() is None:
                    self._json(HTTPStatus.FORBIDDEN, {"error": "Request origin rejected."})
                    return
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-PetCare-Request")
                self.send_header("Access-Control-Max-Age", "600")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                request_path = self._normalized_path()

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
                }.get(target.suffix.lower(), "application/octet-stream")
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

        return Handler