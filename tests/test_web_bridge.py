from __future__ import annotations

import base64
from http.cookiejar import CookieJar
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

from app.database import Database
from app.web_bridge import LocalAdminBridge


PNG_SAMPLE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/"
    "l5sAAAAASUVORK5CYII="
)


def _request(opener, url: str, method: str = "GET", body: dict | None = None):
    headers = {"Origin": url.split("/api", 1)[0]}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
        headers["X-PetCare-Request"] = "1"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        response = opener.open(request, timeout=5)
    except HTTPError as error:
        return error.code, error.headers, error.read()
    return response.status, response.headers, response.read()


def _create_admin_and_supplier(database_path: Path) -> int:
    database = Database(database_path)
    admin_id = database.create_initial_admin(
        "bridge-admin", "Bridge Admin", "StrongPass!2026"
    )
    database.set_actor(admin_id)
    supplier_id = database.save_supplier(
        {"supplier_code": "SUP-WEB-01", "name": "Bridge Supplier"}
    )
    database.create_user(
        "bridge-analyst",
        "Bridge Analyst",
        "AnalystPass!2026",
        "REPORT_ANALYST",
        actor_id=admin_id,
    )
    database.close()
    return supplier_id


def test_local_bridge_allows_same_default_account_for_desktop_and_web(tmp_path: Path):
    database = Database(tmp_path / "default-account.db")
    admin_id = database.create_default_admin()
    database.set_actor(admin_id)
    database.close()

    bridge = LocalAdminBridge(tmp_path / "default-account.db", tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        status, headers, payload = _request(
            opener,
            f"{origin}/api/login",
            "POST",
            {"username": "admin", "password": "admin"},
        )
        assert status == 200
        assert "HttpOnly" in headers.get("Set-Cookie", "")
        session = json.loads(payload)
        assert session["authenticated"] is True
        assert session["must_change_password"] is True

        status, _, session_payload = _request(opener, f"{origin}/api/session")
        assert status == 200
        assert json.loads(session_payload)["must_change_password"] is True
    finally:
        bridge.stop()


def test_local_bridge_auth_import_voucher_and_receipt_attachment(tmp_path: Path):
    supplier_id = _create_admin_and_supplier(tmp_path / "bridge.db")
    bridge = LocalAdminBridge(tmp_path / "bridge.db", tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        opener = build_opener(HTTPCookieProcessor(CookieJar()))

        status, headers, _ = _request(
            opener,
            f"{origin}/api/login",
            "POST",
            {"username": "bridge-admin", "password": "StrongPass!2026"},
        )
        assert status == 200
        assert "HttpOnly" in headers.get("Set-Cookie", "")

        status, _, payload = _request(opener, f"{origin}/api/session")
        session = json.loads(payload)
        assert status == 200
        assert session["user"]["role"] == "ADMIN"
        assert "imports.manage" in session["permissions"]

        status, _, payload = _request(
            opener,
            f"{origin}/api/imports/batches",
            "POST",
            {
                "batch_code": "WEB-IMP-001",
                "supplier_id": supplier_id,
                "import_date": "2026-10-07",
                "note": "Created through local web bridge",
            },
        )
        assert status == 201
        batch_id = json.loads(payload)["id"]

        status, _, payload = _request(
            opener,
            f"{origin}/api/imports/batches/{batch_id}/animals",
            "POST",
            {
                "animal_code": "WEB-PET-001",
                "name": "Bridge Pet",
                "species": "Mèo",
                "breed": "Demo breed",
                "purchase_price": 100000,
                "sale_price": 200000,
                "confirmation": "Handover and image verified.",
                "photoMime": "image/png",
                "photoBase64": base64.b64encode(PNG_SAMPLE).decode("ascii"),
            },
        )
        assert status == 201
        animal_id = json.loads(payload)["animalId"]

        status, _, payload = _request(
            opener, f"{origin}/api/imports/{batch_id}/animals"
        )
        animals = json.loads(payload)["records"]
        assert status == 200
        assert animals[0]["id"] == animal_id
        assert animals[0]["receipt_confirmed"] == 1

        status, headers, attachment = _request(
            opener, f"{origin}/api/intake-receipts/{animal_id}/photo"
        )
        assert status == 200
        assert headers.get("Content-Type") == "image/png"
        assert attachment == PNG_SAMPLE

        status, _, _ = _request(opener, f"{origin}/api/logout", "POST", {})
        assert status == 200
        status, _, _ = _request(
            opener, f"{origin}/api/modules/module_04_pets/records"
        )
        assert status == 401
    finally:
        bridge.stop()


def test_local_bridge_enforces_role_permissions(tmp_path: Path):
    _create_admin_and_supplier(tmp_path / "permissions.db")
    bridge = LocalAdminBridge(tmp_path / "permissions.db", tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            opener,
            f"{origin}/api/login",
            "POST",
            {"username": "bridge-analyst", "password": "AnalystPass!2026"},
        )
        assert status == 200

        status, _, payload = _request(
            opener, f"{origin}/api/modules/module_16_reports/records"
        )
        assert status == 200
        assert json.loads(payload)["source"] == "sqlite"

        status, _, _ = _request(
            opener, f"{origin}/api/modules/module_04_pets/records"
        )
        assert status == 403

        status, _, _ = _request(
            opener,
            f"{origin}/api/imports/batches",
            "POST",
            {
                "batch_code": "FORBIDDEN",
                "supplier_id": 1,
                "import_date": "2026-10-07",
            },
        )
        assert status == 403
    finally:
        bridge.stop()
