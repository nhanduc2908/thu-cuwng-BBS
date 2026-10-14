from __future__ import annotations

import base64
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx


class RemoteDatabaseError(sqlite3.Error):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class _RemoteNamespace:
    def __init__(self, database: "RemoteDatabase", prefix: str) -> None:
        self._database = database
        self._prefix = prefix

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._database._remote_method(f"{self._prefix}.{name}")


class RemoteDatabase:
    """Database-compatible desktop client backed only by the authenticated API."""

    is_remote = True

    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        parsed = urlsplit(base_url.strip())
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValueError("PETCARE_API_URL must be an absolute HTTP(S) URL.")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError(
                "PETCARE_API_URL must not contain credentials, query parameters, or fragments."
            )
        if parsed.scheme != "https" and parsed.hostname not in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise ValueError("Remote desktop connections require HTTPS.")
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=False,
        )
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._user: dict[str, Any] | None = None
        self._permissions: frozenset[str] = frozenset()
        self.actor_id: int | None = None
        self.path = Path("central-api-database")
        self.customers = _RemoteNamespace(self, "customers")
        self.notifications = _RemoteNamespace(self, "notifications")
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RemoteDatabaseError("The central API connection is closed.")

    def _clear_authentication(self) -> None:
        self._token = None
        self._refresh_token = None
        self._user = None
        self._permissions = frozenset()
        self.actor_id = None

    def _refresh_access_token(self) -> None:
        if self._refresh_token is None:
            self._clear_authentication()
            raise PermissionError("Your central PetCare session has expired.")
        try:
            response = self._client.post(
                "/api/auth/refresh",
                headers={"Authorization": f"Bearer {self._refresh_token}"},
            )
        except httpx.HTTPError as error:
            raise RemoteDatabaseError(
                f"Could not refresh the central PetCare session: {error}"
            ) from error
        try:
            payload = response.json()
        except ValueError as error:
            self._clear_authentication()
            raise RemoteDatabaseError(
                "The central API returned invalid session data.",
                response.status_code,
            ) from error
        if not response.is_success:
            self._clear_authentication()
            detail = (
                payload.get("detail", "The central PetCare session has expired.")
                if isinstance(payload, dict)
                else "The central PetCare session has expired."
            )
            if response.status_code == 401:
                raise PermissionError(str(detail))
            raise RemoteDatabaseError(str(detail), response.status_code)
        if not isinstance(payload, dict) or not payload.get("access_token") or not payload.get("refresh_token"):
            self._clear_authentication()
            raise RemoteDatabaseError("The central API returned invalid session data.")
        self._token = str(payload["access_token"])
        self._refresh_token = str(payload["refresh_token"])
        if isinstance(payload.get("user"), dict):
            self._user = dict(payload["user"])
            self.actor_id = int(self._user["id"])
        if isinstance(payload.get("permissions"), list):
            self._permissions = frozenset(map(str, payload["permissions"]))

    @staticmethod
    def _encode(value: Any) -> Any:
        if isinstance(value, bytes):
            return {"__bytes__": base64.b64encode(value).decode("ascii")}
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, tuple):
            return [RemoteDatabase._encode(item) for item in value]
        if isinstance(value, list):
            return [RemoteDatabase._encode(item) for item in value]
        if isinstance(value, dict):
            return {
                str(key): RemoteDatabase._encode(item)
                for key, item in value.items()
            }
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        raise TypeError(f"Unsupported central API argument: {type(value).__name__}")

    @staticmethod
    def _decode(value: Any) -> Any:
        if isinstance(value, list):
            return [RemoteDatabase._decode(item) for item in value]
        if isinstance(value, dict):
            if set(value) == {"__bytes__"}:
                try:
                    return base64.b64decode(value["__bytes__"], validate=True)
                except (ValueError, TypeError) as error:
                    raise RemoteDatabaseError(
                        "The central API returned malformed binary data."
                    ) from error
            return {
                key: RemoteDatabase._decode(item) for key, item in value.items()
            }
        return value

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        self._ensure_open()
        headers: dict[str, str] = {}
        if authenticated:
            if self._token is None:
                raise PermissionError("Sign in to the central PetCare service first.")
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            response = self._client.request(
                method, path, json=json_body, headers=headers
            )
        except httpx.HTTPError as error:
            raise RemoteDatabaseError(
                f"Could not reach the central PetCare service: {error}"
            ) from error
        if response.status_code == 401 and authenticated and self._refresh_token:
            self._refresh_access_token()
            headers["Authorization"] = f"Bearer {self._token}"
            try:
                response = self._client.request(
                    method, path, json=json_body, headers=headers
                )
            except httpx.HTTPError as error:
                raise RemoteDatabaseError(
                    f"Could not reach the central PetCare service: {error}"
                ) from error
        try:
            payload = response.json()
        except ValueError as error:
            raise RemoteDatabaseError(
                f"The central API returned invalid JSON (HTTP {response.status_code}).",
                response.status_code,
            ) from error
        if not response.is_success:
            message = str(payload.get("detail", "Central API request failed."))
            if response.status_code == 403:
                raise PermissionError(message)
            if response.status_code == 401:
                self._clear_authentication()
                raise PermissionError(message)
            raise RemoteDatabaseError(message, response.status_code)
        if not isinstance(payload, dict):
            raise RemoteDatabaseError("The central API returned an invalid response.")
        return payload

    def login(self, username: str, password: str) -> dict[str, Any]:
        self._clear_authentication()
        payload = self._request(
            "POST",
            "/api/auth/login",
            json_body={"username": username, "password": password},
            authenticated=False,
        )
        self._token = str(payload["access_token"])
        self._refresh_token = str(payload["refresh_token"])
        self._user = dict(payload["user"])
        self._permissions = frozenset(map(str, payload.get("permissions", ())))
        self.actor_id = int(self._user["id"])
        return dict(self._user)

    def change_password(self, user_id: int, current: str, new: str, actor_id: int | None = None) -> None:
        if self.actor_id is None or int(user_id) != self.actor_id:
            raise PermissionError("A signed-in user can only change their own password.")
        self._request(
            "POST",
            "/api/auth/change-password",
            json_body={"current_password": current, "new_password": new},
        )
        if self._user is not None:
            self._user["must_change_password"] = False

    def set_actor(self, user_id: int | None) -> None:
        if user_id is not None and self.actor_id != int(user_id):
            raise PermissionError("The central API session belongs to another user.")

    def has_permission(self, user_id: int, permission: str) -> bool:
        if self.actor_id is None or int(user_id) != self.actor_id:
            return False
        return permission in self._permissions

    def _remote_method(self, method_name: str) -> Any:
        def invoke(*args: Any, **kwargs: Any) -> Any:
            payload = self._request(
                "POST",
                "/api/rpc",
                json_body={
                    "method": method_name,
                    "args": self._encode(list(args)),
                    "kwargs": self._encode(kwargs),
                },
            )
            return self._decode(payload.get("result"))

        return invoke

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._remote_method(name)

    def close(self) -> None:
        if not self._closed:
            self._clear_authentication()
            self._client.close()
            self._closed = True
