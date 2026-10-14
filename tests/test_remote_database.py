import json

import httpx
import pytest
from PySide6.QtWidgets import QApplication

from app.database import Database
from app.remote_database import RemoteDatabase
from app.ui.main_window import MainWindow, _UnavailablePage


def test_remote_database_authenticates_and_encodes_binary_rpc_values() -> None:
    database = RemoteDatabase("https://petcare.example.test")
    database._client.close()
    requests: list[httpx.Request] = []
    rpc_attempts = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal rpc_attempts
        requests.append(request)
        if request.url.path == "/api/auth/login":
            return httpx.Response(
                200,
                json={
                    "access_token": "test-token",
                    "refresh_token": "refresh-token",
                    "user": {
                        "id": 4,
                        "username": "staff",
                        "display_name": "Staff",
                        "role": "SALES",
                        "must_change_password": False,
                    },
                    "permissions": ["dashboard.view", "sales.view"],
                },
            )
        if request.url.path == "/api/rpc":
            rpc_attempts += 1
            if rpc_attempts == 1:
                return httpx.Response(401, json={"detail": "expired"})
            return httpx.Response(
                200, json={"result": [{"document": {"__bytes__": "ZmlsZQ=="}}]}
            )
        if request.url.path == "/api/auth/refresh":
            return httpx.Response(
                200,
                json={
                    "access_token": "renewed-token",
                    "refresh_token": "renewed-refresh-token",
                    "expires_in": 1800,
                },
            )
        if request.url.path == "/api/auth/change-password":
            return httpx.Response(200, json={"changed": True})
        return httpx.Response(404, json={"detail": "unknown route"})

    database._client = httpx.Client(
        base_url=database.base_url,
        transport=httpx.MockTransport(respond),
    )
    try:
        user = database.login("staff", "password")
        assert user["id"] == 4
        assert database.actor_id == 4
        assert database.has_permission(4, "sales.view")
        assert not database.has_permission(4, "sales.manage")

        result = database.save_animal({"photo": b"photo"})
        assert result == [{"document": b"file"}]
        rpc_body = json.loads(requests[1].content)
        assert rpc_body["args"] == [{"photo": {"__bytes__": "cGhvdG8="}}]
        assert requests[1].headers["Authorization"] == "Bearer test-token"
        assert requests[2].url.path == "/api/auth/refresh"
        assert requests[2].headers["Authorization"] == "Bearer refresh-token"
        assert requests[3].headers["Authorization"] == "Bearer renewed-token"

        database.change_password(4, "current", "a-long-new-password")
        assert requests[4].url.path == "/api/auth/change-password"
    finally:
        database.close()


def test_remote_database_rejects_plain_http_for_non_loopback_hosts() -> None:
    with pytest.raises(ValueError, match="require HTTPS"):
        RemoteDatabase("http://petcare.example.test")


def test_remote_main_window_does_not_initialize_unpermitted_pages(tmp_path) -> None:
    application = QApplication.instance() or QApplication([])
    database = Database(tmp_path / "remote-ui.db")
    admin_id = database.create_initial_admin(
        "admin", "Administrator", "Administrator!Password42"
    )
    database.set_actor(admin_id)
    analyst_id = database.create_user(
        "analyst",
        "Report Analyst",
        "Analyst!Password42",
        "REPORT_ANALYST",
        admin_id,
    )
    database.set_actor(analyst_id)
    database.is_remote = True
    user = database.authenticate("analyst", "Analyst!Password42")
    assert user is not None

    window = MainWindow(database, user)
    try:
        assert isinstance(window.animals, _UnavailablePage)
        assert isinstance(window.sales, _UnavailablePage)
        assert not isinstance(window.reports, _UnavailablePage)
        assert window.dashboard.cards["TOTAL"].text().isdigit()
    finally:
        window.close()
        application.processEvents()
