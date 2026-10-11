from __future__ import annotations

import base64
from http.cookiejar import CookieJar
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
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


def test_local_bridge_serves_website_pages_and_assets(tmp_path: Path):
    html_root = tmp_path / "HTML"
    assets = html_root / "assets"
    assets.mkdir(parents=True)
    (html_root / "index.html").write_text(
        '<html><link rel="stylesheet" href="assets/site.css">'
        '<script src="assets/site.js"></script></html>',
        encoding="utf-8",
    )
    (assets / "site.css").write_text("body { color: green; }", encoding="utf-8")
    (assets / "site.js").write_text("window.petcare = true;", encoding="utf-8")
    (assets / "logo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8"
    )
    support_folder = "Trang h" + chr(7895) + " tr" + chr(7907)
    support_directory = html_root / support_folder
    support_directory.mkdir()
    (support_directory / "support.html").write_text(
        "<title>PetCare support</title>", encoding="utf-8"
    )
    bridge = LocalAdminBridge(tmp_path / "bridge.db", html_root, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        opener = build_opener()

        status, headers, page = _request(opener, f"{origin}/")
        assert status == 200
        assert headers.get_content_type() == "text/html"
        assert b'assets/site.css' in page

        for asset_path, expected_type in (
            ("/assets/site.css", "text/css"),
            ("/assets/site.js", "text/javascript"),
            ("/assets/logo.svg", "image/svg+xml"),
        ):
            status, headers, _ = _request(opener, f"{origin}{asset_path}")
            assert status == 200
            assert headers.get_content_type() == expected_type

        support_url = f"{origin}/{quote(support_folder)}/support.html"
        status, _, support_page = _request(opener, support_url)
        assert status == 200
        assert b"PetCare support" in support_page

        status, _, _ = _request(opener, f"{origin}/../outside.txt")
        assert status == 404
    finally:
        bridge.stop()


def test_local_bridge_serves_the_split_project_website(tmp_path: Path):
    database = Database(tmp_path / "project-website.db")
    database.close()

    html_root = Path(__file__).resolve().parents[1] / "HTML"
    bridge = LocalAdminBridge(tmp_path / "project-website.db", html_root, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        opener = build_opener()
        paths = (
            "index.html",
            "menu.html",
            "TRrang chính/index.html",
            "TRrang chính/user_portal.html",
            "TRrang chính/petcare_management.html",
            "TRrang chính/nutrition_products_dog.html",
            "Trang hỗ trợ/data_explorer.html",
            "Trang hỗ trợ/admin_store_management.html",
            "Trang hỗ trợ/Module/index.html",
            "styles/petcare_pages.css",
            "scripts/document_language.js",
            "scripts/site_navigation.js",
            "styles/site_navigation.css",
            "data/module_04_pets.json",
            "data/catalog_manifest.json",
        )
        for path in paths:
            status, _, payload = _request(opener, f"{origin}/{quote(path)}")
            assert status == 200, path
            assert payload, path
            if path == "index.html":
                assert b"PetCare Enterprise Console" in payload
                assert b"project_quote.html" in payload
                assert b"Module/index.html" in payload
                assert b"data_explorer.html" in payload
            elif path == "menu.html":
                assert b"TRrang ch" in payload
                assert b"module_17_alerts.html" in payload
                assert b"project_invoice.html" in payload
            elif path == "scripts/site_navigation.js":
                assert b"petcare-global-header" in payload
                assert b"module_17_alerts.html" in payload
                assert b"petcare-page-guide" in payload
                assert "Điểm cần kiểm tra".encode("utf-8") in payload
            elif path == "data/catalog_manifest.json":
                assert b"module_01_platform.json" in payload
                assert b"generated_catalog" in payload
            elif path == "TRrang chính/petcare_management.html":
                assert b'id="moduleGrid"' in payload
                assert b"module_17_alerts.html" in payload
                assert b"module_04_pets.json" in payload
                assert "không phải hồ sơ khách hàng thật" in payload.decode("utf-8")
            elif path == "TRrang chính/user_portal.html":
                assert b"/api/customer/" in payload
                assert b'api("portal")' in payload
                assert b"data-auth-form" in payload
                assert b"petcare_customer_session" not in payload
                assert b"role-select" not in payload
                assert b"Pepper" not in payload
            elif path == "Trang hỗ trợ/data_explorer.html":
                assert b"catalog_manifest.json" in payload
                assert "Chọn nguồn dữ liệu".encode("utf-8") in payload
                assert b"exportCsv" in payload
    finally:
        bridge.stop()


def test_dataset_workspace_supports_import_crud_archive_and_permission_checks(tmp_path: Path):
    html_root = tmp_path / "HTML"
    data_directory = html_root / "data"
    data_directory.mkdir(parents=True)
    dataset_path = data_directory / "module_04_pets.json"
    original_dataset = {
        "meta": {"synthetic": True},
        "demoData": [{"animalId": "PET-001", "displayName": "Demo Pet"}],
    }
    dataset_path.write_text(json.dumps(original_dataset), encoding="utf-8")

    database_path = tmp_path / "dataset-workspace.db"
    database = Database(database_path)
    admin_id = database.create_initial_admin(
        "dataset-admin", "Dataset Admin", "StrongPass!2026"
    )
    database.create_user(
        "dataset-analyst",
        "Dataset Analyst",
        "AnalystPass!2026",
        "REPORT_ANALYST",
        actor_id=admin_id,
    )
    database.close()

    bridge = LocalAdminBridge(database_path, html_root, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        admin = build_opener(HTTPCookieProcessor(CookieJar()))
        dataset_url = f"{origin}/api/datasets/module_04_pets/records"
        status, _, _ = _request(admin, dataset_url)
        assert status == 401

        status, _, _ = _request(
            admin,
            f"{origin}/api/login",
            "POST",
            {"username": "dataset-admin", "password": "StrongPass!2026"},
        )
        assert status == 200

        status, _, payload = _request(admin, f"{dataset_url}?source=file")
        assert status == 200
        assert json.loads(payload)["records"][0]["record"]["animalId"] == "PET-001"

        status, _, payload = _request(
            admin,
            f"{dataset_url}?source=file",
            "POST",
            {"record": {"animalId": "PET-002", "displayName": "New Pet"}},
        )
        assert status == 201
        file_record_id = json.loads(payload)["id"]

        status, _, payload = _request(
            admin,
            f"{origin}/api/datasets/module_04_pets/import?source=sqlite",
            "POST",
            {},
        )
        assert status == 200
        assert json.loads(payload)["inserted"] == 2

        sqlite_url = f"{dataset_url}?source=sqlite"
        status, _, payload = _request(admin, sqlite_url)
        assert status == 200
        imported = json.loads(payload)["records"]
        sqlite_record_id = imported[0]["id"]
        assert len(imported) == 2

        status, _, _ = _request(
            admin,
            f"{origin}/api/datasets/module_04_pets/records/{sqlite_record_id}?source=sqlite",
            "PUT",
            {"record": {"animalId": "PET-001", "displayName": "Edited in SQLite"}},
        )
        assert status == 200
        status, _, payload = _request(admin, sqlite_url)
        assert json.loads(payload)["records"][0]["record"]["displayName"] == "Edited in SQLite"

        status, _, _ = _request(
            admin,
            f"{origin}/api/datasets/module_04_pets/records/{file_record_id}?source=file",
            "DELETE",
            {},
        )
        assert status == 200
        assert len(list((tmp_path / "dataset_backups").glob("module_04_pets-*.json"))) == 2
        assert json.loads(dataset_path.read_text(encoding="utf-8"))["demoData"][file_record_id]["_archived"]

        analyst = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            analyst,
            f"{origin}/api/login",
            "POST",
            {"username": "dataset-analyst", "password": "AnalystPass!2026"},
        )
        assert status == 200
        status, _, _ = _request(analyst, dataset_url)
        assert status == 403
        status, _, _ = _request(
            analyst,
            f"{origin}/api/datasets/module_04_pets/records?source=file",
            "POST",
            {"record": {"animalId": "UNAUTHORIZED"}},
        )
        assert status == 403
    finally:
        bridge.stop()


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


def test_customer_portal_registration_approval_invite_and_scoped_records(tmp_path: Path):
    database_path = tmp_path / "customer-portal.db"
    database = Database(database_path)
    admin_id = database.create_initial_admin(
        "portal-admin", "Portal Admin", "StrongPass!2026"
    )
    database.create_user(
        "portal-analyst",
        "Portal Analyst",
        "AnalystPass!2026",
        "REPORT_ANALYST",
        actor_id=admin_id,
    )
    database.set_actor(admin_id)
    customer_one = database.save_customer(
        {"customer_code": "PORTAL-001", "name": "Customer One", "phone": "111"}
    )
    customer_two = database.save_customer(
        {"customer_code": "PORTAL-002", "name": "Customer Two", "phone": "222"}
    )
    customer_three = database.save_customer(
        {"customer_code": "PORTAL-003", "name": "Customer Three", "phone": "333"}
    )
    database.customers.save_pet(
        {"customer_id": customer_one, "name": "Pet One", "species": "Dog"}
    )
    database.customers.save_pet(
        {"customer_id": customer_two, "name": "Pet Two", "species": "Cat"}
    )
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        anonymous = build_opener(HTTPCookieProcessor(CookieJar()))
        portal_url = f"{origin}/api/customer/portal"
        status, _, _ = _request(anonymous, portal_url)
        assert status == 401
        status, _, _ = _request(
            anonymous,
            f"{origin}/api/customer/register",
            "POST",
            {
                "username": "waiting-customer",
                "display_name": "Waiting Customer",
                "password": "CustomerPass!2026",
                "customer_id": customer_one,
            },
        )
        assert status == 202
        database = Database(database_path)
        pending_link = database.connection.execute(
            "SELECT customer_id, status FROM customer_portal_accounts WHERE username = ?",
            ("waiting-customer",),
        ).fetchone()
        assert pending_link["customer_id"] is None
        assert pending_link["status"] == "PENDING"
        database.close()
        status, _, payload = _request(
            anonymous,
            f"{origin}/api/customer/login",
            "POST",
            {"username": "waiting-customer", "password": "CustomerPass!2026"},
        )
        assert status == 403
        assert json.loads(payload)["pendingApproval"] is True

        staff = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            staff,
            f"{origin}/api/login",
            "POST",
            {"username": "portal-admin", "password": "StrongPass!2026"},
        )
        assert status == 200
        status, _, payload = _request(
            staff, f"{origin}/api/customer/accounts?status=pending"
        )
        assert status == 200
        assert json.loads(payload)["records"][0]["username"] == "waiting-customer"
        analyst = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            analyst,
            f"{origin}/api/login",
            "POST",
            {"username": "portal-analyst", "password": "AnalystPass!2026"},
        )
        assert status == 200
        status, _, _ = _request(
            analyst, f"{origin}/api/customer/accounts?status=pending"
        )
        assert status == 403
        status, _, _ = _request(
            analyst,
            f"{origin}/api/customer/invites",
            "POST",
            {"customer_id": customer_three},
        )
        assert status == 403
        database = Database(database_path)
        pending_account_id = database.connection.execute(
            "SELECT id FROM customer_portal_accounts WHERE username = ?",
            ("waiting-customer",),
        ).fetchone()["id"]
        database.close()
        status, _, _ = _request(
            staff,
            f"{origin}/api/customer/accounts/{pending_account_id}/approve",
            "POST",
            {"customer_id": customer_two},
        )
        assert status == 200

        approved_customer = build_opener(HTTPCookieProcessor(CookieJar()))
        status, headers, _ = _request(
            approved_customer,
            f"{origin}/api/customer/login",
            "POST",
            {"username": "waiting-customer", "password": "CustomerPass!2026"},
        )
        assert status == 200
        cookie = headers.get("Set-Cookie", "")
        assert "petcare_customer_session=" in cookie
        assert "HttpOnly" in cookie
        assert "SameSite=Strict" in cookie
        assert "Max-Age=" in cookie
        status, _, payload = _request(approved_customer, portal_url)
        assert status == 200
        customer_two_portal = json.loads(payload)
        assert customer_two_portal["customer"]["customer_code"] == "PORTAL-002"
        assert [pet["name"] for pet in customer_two_portal["pets"]] == ["Pet Two"]

        status, _, invite_payload = _request(
            staff,
            f"{origin}/api/customer/invites",
            "POST",
            {"customer_id": customer_one},
        )
        assert status == 201
        invite = json.loads(invite_payload)
        invite_code = invite["invite_code"]
        status, _, payload = _request(
            staff, f"{origin}/api/customer/invites?status=active"
        )
        assert status == 200
        assert json.loads(payload)["records"][0]["id"] == invite["id"]
        invited_customer = build_opener(HTTPCookieProcessor(CookieJar()))
        status, headers, _ = _request(
            invited_customer,
            f"{origin}/api/customer/accept-invite",
            "POST",
            {
                "invite_code": invite_code,
                "username": "invited-customer",
                "display_name": "Invited Customer",
                "password": "InvitePass!2026",
                "customer_id": customer_two,
            },
        )
        assert status == 201
        assert "petcare_customer_session=" in headers.get("Set-Cookie", "")
        status, _, payload = _request(invited_customer, portal_url)
        assert status == 200
        customer_one_portal = json.loads(payload)
        assert customer_one_portal["customer"]["customer_code"] == "PORTAL-001"
        assert [pet["name"] for pet in customer_one_portal["pets"]] == ["Pet One"]
        assert "Pet Two" not in json.dumps(customer_one_portal)
        status, _, _ = _request(
            invited_customer,
            f"{origin}/api/customer/logout",
            "POST",
            {},
        )
        assert status == 200
        status, _, _ = _request(invited_customer, f"{origin}/api/customer/session")
        assert status == 401

        replay = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            replay,
            f"{origin}/api/customer/accept-invite",
            "POST",
            {
                "invite_code": invite_code,
                "username": "invite-replay",
                "display_name": "Replay",
                "password": "InvitePass!2026",
            },
        )
        assert status == 400

        status, _, _ = _request(
            anonymous,
            f"{origin}/api/customer/register",
            "POST",
            {
                "username": "reject-customer",
                "display_name": "Reject Customer",
                "password": "CustomerPass!2026",
            },
        )
        assert status == 202
        database = Database(database_path)
        rejected_account_id = database.connection.execute(
            "SELECT id FROM customer_portal_accounts WHERE username = ?",
            ("reject-customer",),
        ).fetchone()["id"]
        database.close()
        status, _, _ = _request(
            staff,
            f"{origin}/api/customer/accounts/{rejected_account_id}/reject",
            "POST",
            {},
        )
        assert status == 200

        status, _, second_invite_payload = _request(
            staff,
            f"{origin}/api/customer/invites",
            "POST",
            {"customer_id": customer_three},
        )
        assert status == 201
        second_invite = json.loads(second_invite_payload)
        status, _, _ = _request(
            staff,
            f"{origin}/api/customer/invites/{second_invite['id']}/expire",
            "POST",
            {},
        )
        assert status == 200
    finally:
        bridge.stop()


def test_customer_portal_is_disabled_on_non_loopback_binding(tmp_path: Path):
    bridge = LocalAdminBridge(tmp_path / "non-loopback.db", tmp_path, host="0.0.0.0", port=0)
    bridge.start()
    try:
        port = bridge._server.server_address[1]
        opener = build_opener()
        status, _, payload = _request(
            opener, f"http://127.0.0.1:{port}/api/customer/session"
        )
        assert status == 403
        assert "loopback-bound" in json.loads(payload)["error"]
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
