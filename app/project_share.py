from __future__ import annotations

from collections import defaultdict, deque
from contextlib import contextmanager
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import logging
import mimetypes
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from typing import Iterator
from urllib.parse import parse_qs, unquote, urlsplit

from app.modules.audit.repository import AuditRepository
from app.modules.auth.repository import AuthRepository


LOGGER = logging.getLogger("pet_store.project_share")
READ_ONLY_ROLES = frozenset({"REPORT_ANALYST", "AUDITOR"})
SESSION_COOKIE = "petcare_project_viewer"
SESSION_IDLE_SECONDS = 30 * 60
LOGIN_WINDOW_SECONDS = 60
MAX_LOGIN_ATTEMPTS = 5
MAX_FORM_BYTES = 4096
ALLOWED_EXTENSIONS = frozenset({
    ".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
    ".webp", ".gif", ".ico", ".woff", ".woff2", ".ttf",
})


class _ThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class ProjectShareServer:
    """Authenticated, read-only sharing for the static project website."""

    def __init__(
        self,
        database_path: str | Path,
        project_root: str | Path,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        self.database_path = Path(database_path).resolve()
        self.project_root = Path(project_root).resolve()
        self.html_root = (self.project_root / "HTML").resolve()
        self.host = host
        self.port = port
        self._server: _ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._startup_error: BaseException | None = None
        self._sessions: dict[str, dict[str, object]] = {}
        self._failed_logins: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @property
    def base_url(self) -> str | None:
        if self._server is None:
            return None
        address, port = self._server.server_address[:2]
        return f"http://{address}:{port}"

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, timeout: float = 10.0) -> str:
        if self.is_running and self.base_url:
            return self.base_url
        if self.host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Project share must bind to loopback only.")
        if not (self.project_root.is_dir() and self.html_root.is_dir()):
            raise FileNotFoundError("Project root and HTML directory must exist.")

        self._ready.clear()
        self._startup_error = None
        self._thread = threading.Thread(
            target=self._serve,
            name="PetCareProjectShare",
            daemon=True,
        )
        self._thread.start()
        if not self._ready.wait(timeout):
            raise TimeoutError("Project share server did not start in time.")
        if self._startup_error is not None:
            raise OSError("Project share server failed to start.") from self._startup_error
        if self.base_url is None:
            raise OSError("Project share server stopped during startup.")
        return self.base_url

    def stop(self, timeout: float = 5.0) -> None:
        server = self._server
        if server is not None:
            server.shutdown()
            server.server_close()
        thread = self._thread
        if thread is not None:
            thread.join(timeout)
        if thread is not None and thread.is_alive():
            LOGGER.warning("Project share server did not stop before timeout.")
        self._server = None
        self._thread = None
        with self._lock:
            self._sessions.clear()

    def _serve(self) -> None:
        server: _ThreadingHTTPServer | None = None
        try:
            server = _ThreadingHTTPServer(
                (self.host, self.port), self._handler_type()
            )
            self._server = server
            self._ready.set()
            LOGGER.info("Read-only project share started at %s", self.base_url)
            server.serve_forever(poll_interval=0.2)
        except BaseException as error:
            self._startup_error = error
            self._ready.set()
            LOGGER.exception("Project share server stopped unexpectedly")
        finally:
            if server is not None:
                server.server_close()
            self._server = None

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def _handler_type(self) -> type[BaseHTTPRequestHandler]:
        share = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "PetCareProjectView"
            sys_version = ""

            def log_message(self, format_string: str, *args: object) -> None:
                LOGGER.info("%s - %s", self.address_string(), format_string % args)

            def end_headers(self) -> None:
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header("Referrer-Policy", "same-origin")
                self.send_header("Cache-Control", "no-store")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'self' data:; script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
                    "font-src 'self' data:; connect-src 'self'; object-src 'none'; "
                    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
                )
                super().end_headers()

            def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)

            def _text(self, status: HTTPStatus, message: str) -> None:
                self._send(status, message.encode("utf-8"), "text/plain; charset=utf-8")

            def _origin_is_same(self) -> bool:
                origin = self.headers.get("Origin")
                if not origin:
                    return False
                parsed = urlsplit(origin)
                expected_host = self.headers.get(
                    "X-Forwarded-Host", self.headers.get("Host", "")
                ).lower()
                forwarded_proto = self.headers.get("X-Forwarded-Proto", "").lower()
                expected_scheme = "https" if forwarded_proto == "https" else "http"
                return (
                    parsed.scheme == expected_scheme
                    and parsed.netloc.lower() == expected_host
                )

            def _cookie_value(self) -> str | None:
                for part in self.headers.get("Cookie", "").split(";"):
                    name, separator, value = part.strip().partition("=")
                    if separator and name == SESSION_COOKIE:
                        return value
                return None

            def _session(self) -> dict[str, object] | None:
                token = self._cookie_value()
                if not token:
                    return None
                now = time.monotonic()
                with share._lock:
                    session = share._sessions.get(token)
                    if session is None or now - float(session["last_seen"]) > SESSION_IDLE_SECONDS:
                        share._sessions.pop(token, None)
                        return None
                    session["last_seen"] = now
                try:
                    with share._connect() as connection:
                        user = connection.execute(
                            "SELECT role, is_active, must_change_password FROM users WHERE id = ?",
                            (session["user_id"],),
                        ).fetchone()
                except sqlite3.Error:
                    LOGGER.exception("Unable to validate project viewer session")
                    return None
                if (
                    user is None
                    or not user["is_active"]
                    or user["must_change_password"]
                    or user["role"] not in READ_ONLY_ROLES
                ):
                    with share._lock:
                        share._sessions.pop(token, None)
                    return None
                return session

            def _login_page(self, error: str = "") -> bytes:
                error_html = (
                    f'<p class="error" role="alert">{html.escape(error)}</p>'
                    if error else ""
                )
                page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="same-origin">
<title>Đăng nhập xem PetCare</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:18px;background:#f2f7f2;color:#19352b;font:15px/1.6 "Segoe UI",Arial,sans-serif}}
main{{width:min(440px,100%);padding:26px;border:1px solid #dce8df;border-radius:18px;background:#fff;box-shadow:0 16px 42px #14362412}}
h1{{margin:0 0 5px;font-size:1.5rem}}p{{color:#667a70;font-size:.88rem}}label{{display:grid;gap:5px;margin:13px 0;color:#456153;font-size:.8rem;font-weight:750}}
input{{min-height:43px;padding:9px 11px;border:1px solid #dce8df;border-radius:9px;font:inherit}}button{{width:100%;min-height:44px;margin-top:8px;border:0;border-radius:9px;background:#1c684a;color:#fff;font:inherit;font-weight:800;cursor:pointer}}
.error{{padding:9px 11px;border-radius:8px;background:#fbe9e5;color:#813f32}}.note{{margin-top:16px;padding-top:12px;border-top:1px solid #eaf0eb;font-size:.74rem}}
</style></head><body><main><h1>PetCare · Chế độ quan sát</h1>
<p>Đăng nhập bằng tài khoản riêng có vai trò Chuyên viên báo cáo hoặc Kiểm toán viên. Chỉ phục vụ website/báo cáo tĩnh; không hiển thị database nghiệp vụ.</p>
{error_html}<form method="post" action="/share/login">
<label>Tên đăng nhập<input name="username" autocomplete="username" required maxlength="64"></label>
<label>Mật khẩu<input name="password" type="password" autocomplete="current-password" required maxlength="1024"></label>
<button type="submit">Đăng nhập để quan sát</button></form>
<p class="note">Phiên xem có thời hạn không hoạt động 30 phút. Truy cập thành công/thất bại được ghi vào nhật ký hệ thống.</p></main></body></html>"""
                return page.encode("utf-8")

            def _login(self) -> None:
                if not self._origin_is_same():
                    self._text(HTTPStatus.FORBIDDEN, "Origin không hợp lệ.")
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    self._text(HTTPStatus.BAD_REQUEST, "Form không hợp lệ.")
                    return
                if length < 1 or length > MAX_FORM_BYTES:
                    self._text(HTTPStatus.BAD_REQUEST, "Kích thước form không hợp lệ.")
                    return
                remote = self.client_address[0]
                now = time.monotonic()
                with share._lock:
                    attempts = share._failed_logins[remote]
                    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
                        attempts.popleft()
                    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
                        self._text(HTTPStatus.TOO_MANY_REQUESTS, "Thử lại sau một phút.")
                        return
                try:
                    form = parse_qs(
                        self.rfile.read(length).decode("utf-8", errors="replace"),
                        keep_blank_values=True,
                        max_num_fields=4,
                    )
                except ValueError:
                    self._text(HTTPStatus.BAD_REQUEST, "Form không hợp lệ.")
                    return
                username = (form.get("username") or [""])[0].strip()[:64]
                password = (form.get("password") or [""])[0]
                user: dict[str, object] | None = None
                try:
                    with share._connect() as connection:
                        user = AuthRepository(connection).authenticate(username, password)
                        audit = AuditRepository(connection)
                        if (
                            user is not None
                            and user["role"] in READ_ONLY_ROLES
                            and not user["must_change_password"]
                        ):
                            audit.record(
                                int(user["id"]),
                                "PROJECT_SHARE_LOGIN",
                                "project_share",
                                details=f"client={remote}",
                            )
                        else:
                            user = None
                            audit.record(
                                None,
                                "PROJECT_SHARE_LOGIN_FAILED",
                                "project_share",
                                details=f"username={username}; client={remote}",
                            )
                except (sqlite3.Error, ValueError):
                    LOGGER.exception("Project viewer authentication failed unexpectedly")
                    self._text(HTTPStatus.INTERNAL_SERVER_ERROR, "Không thể xác thực lúc này.")
                    return

                if user is None:
                    with share._lock:
                        share._failed_logins[remote].append(now)
                    self._send(
                        HTTPStatus.UNAUTHORIZED,
                        self._login_page(
                            "Thông tin không đúng hoặc tài khoản chưa được cấp quyền xem."
                        ),
                        "text/html; charset=utf-8",
                    )
                    return

                token = secrets.token_urlsafe(32)
                with share._lock:
                    share._failed_logins.pop(remote, None)
                    share._sessions[token] = {
                        "user_id": int(user["id"]),
                        "username": str(user["username"]),
                        "last_seen": time.monotonic(),
                    }
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/SC.HTML")
                secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "").lower() == "https" else ""
                self.send_header(
                    "Set-Cookie",
                    f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Strict; Path=/; "
                    f"Max-Age={SESSION_IDLE_SECONDS}{secure}",
                )
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _logout(self) -> None:
                if not self._origin_is_same():
                    self._text(HTTPStatus.FORBIDDEN, "Origin không hợp lệ.")
                    return
                token = self._cookie_value()
                session = self._session()
                if token:
                    with share._lock:
                        share._sessions.pop(token, None)
                if session:
                    try:
                        with share._connect() as connection:
                            AuditRepository(connection).record(
                                int(session["user_id"]),
                                "PROJECT_SHARE_LOGOUT",
                                "project_share",
                            )
                    except sqlite3.Error:
                        LOGGER.exception("Unable to audit project viewer logout")
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/")
                self.send_header(
                    "Set-Cookie",
                    f"{SESSION_COOKIE}=; HttpOnly; SameSite=Strict; Path=/; "
                    f"Max-Age=0"
                    f"{'; Secure' if self.headers.get('X-Forwarded-Proto', '').lower() == 'https' else ''}",
                )
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _static_path(self) -> Path | None:
                request_path = unquote(urlsplit(self.path).path)
                if "\x00" in request_path or "\\" in request_path:
                    return None
                if request_path in {"/", "/SC.HTML"}:
                    candidate = share.project_root / "SC.HTML"
                else:
                    relative = request_path.lstrip("/")
                    if not relative.startswith("HTML/"):
                        return None
                    candidate = share.project_root / relative
                try:
                    resolved = candidate.resolve(strict=True)
                    resolved.relative_to(share.project_root)
                except (OSError, ValueError):
                    return None
                if (
                    not resolved.is_file()
                    or resolved.suffix.lower() not in ALLOWED_EXTENSIONS
                    or (resolved != share.project_root / "SC.HTML"
                        and share.html_root not in resolved.parents)
                ):
                    return None
                return resolved

            def _serve_static(self) -> None:
                request_path = urlsplit(self.path).path
                if request_path.startswith("/api/") or request_path.startswith("/customer/"):
                    self._text(HTTPStatus.NOT_FOUND, "Not found.")
                    return
                if request_path == "/share/logout":
                    self._text(HTTPStatus.METHOD_NOT_ALLOWED, "POST required.")
                    return
                if self._session() is None:
                    self.send_response(HTTPStatus.UNAUTHORIZED)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    body = self._login_page()
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    if self.command != "HEAD":
                        self.wfile.write(body)
                    return
                path = self._static_path()
                if path is None:
                    self._text(HTTPStatus.NOT_FOUND, "Not found.")
                    return
                try:
                    content = path.read_bytes()
                except OSError:
                    LOGGER.exception("Unable to read shared project file")
                    self._text(HTTPStatus.INTERNAL_SERVER_ERROR, "Unable to read file.")
                    return
                if path.suffix.lower() == ".html":
                    try:
                        page = content.decode("utf-8")
                    except UnicodeDecodeError:
                        LOGGER.exception("Shared HTML page is not valid UTF-8: %s", path)
                        self._text(HTTPStatus.INTERNAL_SERVER_ERROR, "Invalid HTML encoding.")
                        return
                    logout_bar = (
                        '<form method="post" action="/share/logout" '
                        'style="position:fixed;right:12px;bottom:12px;z-index:99999">'
                        '<button type="submit" style="padding:9px 12px;border:1px solid #cbd9cf;'
                        'border-radius:9px;background:#fff;color:#1c684a;font:700 13px Segoe UI,Arial,sans-serif;'
                        'box-shadow:0 4px 16px #183f2b20">Thoát chế độ quan sát</button></form>'
                    )
                    page, _ = re.subn(
                        r"</body\s*>",
                        lambda match: logout_bar + match.group(0),
                        page,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    content = page.encode("utf-8")
                content_type, _ = mimetypes.guess_type(path.name)
                if content_type is None:
                    content_type = "application/octet-stream"
                if content_type.startswith("text/") or content_type in {
                    "application/javascript", "application/json", "image/svg+xml"
                }:
                    content_type += "; charset=utf-8"
                self._send(HTTPStatus.OK, content, content_type)

            def do_GET(self) -> None:
                path = urlsplit(self.path).path
                if path == "/share/login":
                    self._send(HTTPStatus.METHOD_NOT_ALLOWED, b"POST required.", "text/plain")
                    return
                self._serve_static()

            def do_HEAD(self) -> None:
                self._serve_static()

            def do_POST(self) -> None:
                path = urlsplit(self.path).path
                if path == "/share/login":
                    self._login()
                elif path == "/share/logout":
                    self._logout()
                else:
                    self._text(HTTPStatus.METHOD_NOT_ALLOWED, "Read-only share.")

            def do_PUT(self) -> None:
                self._text(HTTPStatus.METHOD_NOT_ALLOWED, "Read-only share.")

            def do_PATCH(self) -> None:
                self._text(HTTPStatus.METHOD_NOT_ALLOWED, "Read-only share.")

            def do_DELETE(self) -> None:
                self._text(HTTPStatus.METHOD_NOT_ALLOWED, "Read-only share.")

            def do_OPTIONS(self) -> None:
                self._text(HTTPStatus.METHOD_NOT_ALLOWED, "Read-only share.")

        return Handler
