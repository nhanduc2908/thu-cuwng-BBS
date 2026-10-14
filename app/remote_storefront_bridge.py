from __future__ import annotations

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import threading
from urllib.parse import urlsplit

import httpx


LOGGER = logging.getLogger("pet_store.remote_storefront")
MAX_ORDER_REQUEST_BYTES = 64 * 1024
STOREFRONT_PREFIX = "/api/storefront/"


class RemoteStorefrontBridge:
    """Serve storefront assets locally and proxy storefront traffic to the API."""

    def __init__(
        self,
        base_url: str,
        html_root: str | Path,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        self.api_base_url = base_url.rstrip("/")
        self.html_root = Path(html_root).resolve()
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def local_url(self) -> str | None:
        if self._server is None:
            return None
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    @property
    def base_url(self) -> str:
        return self.local_url or f"http://{self.host}:{self.port}"

    def start(self) -> str:
        if self._server is not None:
            assert self.local_url is not None
            return self.local_url
        bridge = self

        class Handler(SimpleHTTPRequestHandler):
            server_version = "PetCareRemoteStorefront/1.0"

            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, directory=str(bridge.html_root), **kwargs)

            def log_message(self, format_string: str, *args: object) -> None:
                LOGGER.info("%s - %s", self.address_string(), format_string % args)

            def do_GET(self) -> None:
                path = urlsplit(self.path).path
                if path.startswith(STOREFRONT_PREFIX):
                    if path != f"{STOREFRONT_PREFIX}catalog" and not path.startswith(
                        f"{STOREFRONT_PREFIX}order-requests/"
                    ):
                        self._json(
                            HTTPStatus.NOT_FOUND,
                            {"detail": "Unknown storefront endpoint."},
                        )
                        return
                    self._proxy("GET", path)
                    return
                super().do_GET()

            def do_POST(self) -> None:
                path = urlsplit(self.path).path
                if path != f"{STOREFRONT_PREFIX}order-requests":
                    self._json(
                        HTTPStatus.NOT_FOUND,
                        {"detail": "Unknown storefront endpoint."},
                    )
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    self._json(HTTPStatus.BAD_REQUEST, {"detail": "Invalid body size."})
                    return
                if length < 1 or length > MAX_ORDER_REQUEST_BYTES:
                    self._json(
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                        {"detail": "Order request is missing or too large."},
                    )
                    return
                body = self.rfile.read(length)
                try:
                    parsed_body = json.loads(body)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self._json(
                        HTTPStatus.BAD_REQUEST,
                        {"detail": "A JSON order request is required."},
                    )
                    return
                if not isinstance(parsed_body, dict):
                    self._json(
                        HTTPStatus.BAD_REQUEST,
                        {"detail": "A JSON order object is required."},
                    )
                    return
                self._proxy("POST", path, parsed_body)

            def _proxy(
                self, method: str, path: str, body: dict[str, object] | None = None
            ) -> None:
                try:
                    with httpx.Client(
                        base_url=bridge.api_base_url,
                        timeout=20.0,
                        follow_redirects=False,
                    ) as client:
                        response = client.request(method, path, json=body)
                except httpx.HTTPError:
                    LOGGER.exception("Remote storefront API request failed: %s", path)
                    self._json(
                        HTTPStatus.BAD_GATEWAY,
                        {"detail": "Could not reach the central PetCare API."},
                    )
                    return
                content_type = response.headers.get(
                    "content-type", "application/json; charset=utf-8"
                )
                self.send_response(response.status_code)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(response.content)))
                self.end_headers()
                self.wfile.write(response.content)

            def _json(self, status: HTTPStatus, payload: dict[str, str]) -> None:
                content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header(
                    "Content-Type", "application/json; charset=utf-8"
                )
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        server = ThreadingHTTPServer((self.host, self.port), Handler)
        server.daemon_threads = True
        server.timeout = 0.25
        self._server = server
        self._thread = threading.Thread(
            target=server.serve_forever,
            name="PetCareRemoteStorefrontBridge",
            daemon=True,
        )
        self._thread.start()
        local_url = self.local_url
        if local_url is None:
            self.stop()
            raise RuntimeError("Could not determine the remote storefront bridge URL.")
        return local_url

    def stop(self, timeout: float = 5.0) -> None:
        server, self._server = self._server, None
        thread, self._thread = self._thread, None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout)
