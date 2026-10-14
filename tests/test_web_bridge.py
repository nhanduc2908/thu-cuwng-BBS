from __future__ import annotations

import base64
from datetime import date
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
            "Phiếu xuất/index.html",
            "Phiếu xuất/phieu-xuat-hang.html",
            "Phiếu xuất/doi-hang-loi-cho-khach.html",
            "scripts/store_slip_form.js",
            "scripts/store_slip_index.js",
            "styles/store_slip.css",
            "data/store_slips_catalog.json",
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
            elif path == "Phiếu xuất/phieu-xuat-hang.html":
                assert b"/sales/orders/" in payload
                assert b"/store/slips" in payload
                assert b"window.print()" in payload
                assert "không phải hóa đơn điện tử".encode("utf-8") in payload
            elif path == "Phiếu xuất/index.html":
                assert "40 mẫu".encode("utf-8") in payload
            elif path == "Phiếu xuất/doi-hang-loi-cho-khach.html":
                assert b'data-slip-type="doi-hang-loi-cho-khach"' in payload
            elif path == "scripts/store_slip_form.js":
                assert b"/store/slip-types/" in payload
                assert b"/store/slips" in payload
            elif path == "data/store_slips_catalog.json":
                assert len(json.loads(payload)) == 40
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


def test_dispatch_details_require_sales_permission_and_only_return_requested_order(tmp_path: Path):
    database_path = tmp_path / "dispatch.db"
    database = Database(database_path)
    admin_id = database.create_initial_admin(
        "dispatch-admin", "Dispatch Admin", "StrongPass!2026"
    )
    database.create_user(
        "dispatch-sales",
        "Dispatch Sales",
        "SalesPass!2026",
        "SALES",
        actor_id=admin_id,
    )
    database.create_user(
        "dispatch-analyst",
        "Dispatch Analyst",
        "AnalystPass!2026",
        "REPORT_ANALYST",
        actor_id=admin_id,
    )
    database.set_actor(admin_id)
    customer_id = database.save_customer({
        "customer_code": "CUS-DISPATCH",
        "name": "Nguyễn An",
        "phone": "0900000000",
        "email": "an@example.test",
        "address": "Hà Nội",
        "note": "",
    })
    animal_ids = []
    order_ids = []
    for index in range(2):
        animal_ids.append(database.save_animal({
            "animal_code": f"PET-DISPATCH-{index}",
            "name": f"Milo {index}",
            "species": "Mèo",
            "breed": "Mèo ta",
            "gender": "Đực",
            "birth_date": "2025-01-10",
            "color": "Vàng",
            "weight": 3.5,
            "origin": "Trong nước",
            "purchase_price": 1_000_000,
            "sale_price": 2_000_000,
            "status": "AVAILABLE",
            "health_status": "Bình thường",
            "description": "",
        }))
        order_id = database.create_sales_order({
            "order_code": f"SO-DISPATCH-{index}",
            "customer_id": customer_id,
            "animal_ids": [animal_ids[-1]],
            "ordered_at": "2026-01-02",
            "note": "",
        })
        order_ids.append(order_id)
    database.add_payment(order_ids[0], {
        "amount": 2_000_000,
        "method": "BANK_TRANSFER",
        "paid_at": "2026-01-03",
        "reference": "private-reference",
        "note": "private-payment-note",
    })
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path / "HTML", port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        dispatch_url = f"{origin}/api/sales/orders/{order_ids[0]}/dispatch"
        anonymous = build_opener()
        status, _, _ = _request(anonymous, dispatch_url)
        assert status == 401

        analyst = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            analyst,
            f"{origin}/api/login",
            "POST",
            {"username": "dispatch-analyst", "password": "AnalystPass!2026"},
        )
        assert status == 200
        status, _, _ = _request(analyst, dispatch_url)
        assert status == 403

        sales = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            sales,
            f"{origin}/api/login",
            "POST",
            {"username": "dispatch-sales", "password": "SalesPass!2026"},
        )
        assert status == 200
        status, _, payload = _request(sales, dispatch_url)
        assert status == 200
        details = json.loads(payload)
        assert details["order"]["id"] == order_ids[0]
        assert details["order"]["status"] == "PAID"
        assert details["issuable"] is True
        assert details["paid_amount"] == 2_000_000
        assert details["balance"] == 0
        assert [item["animal_code"] for item in details["animals"]] == ["PET-DISPATCH-0"]
        assert "private-reference" not in payload.decode("utf-8")
        assert "private-payment-note" not in payload.decode("utf-8")

        status, _, payload = _request(
            sales, f"{origin}/api/sales/orders/{order_ids[1]}/dispatch"
        )
        assert status == 200
        unpaid = json.loads(payload)
        assert unpaid["order"]["id"] == order_ids[1]
        assert unpaid["issuable"] is False
        assert unpaid["paid_amount"] == 0
        assert [item["animal_code"] for item in unpaid["animals"]] == ["PET-DISPATCH-1"]

        status, _, _ = _request(sales, f"{origin}/api/sales/orders/999999/dispatch")
        assert status == 404
    finally:
        bridge.stop()


def test_store_slip_records_are_persisted_and_permission_scoped(tmp_path: Path):
    database_path = tmp_path / "store-slips.db"
    database = Database(database_path)
    admin_id = database.create_initial_admin(
        "slip-admin", "Slip Admin", "StrongPass!2026"
    )
    database.create_user(
        "slip-sales", "Slip Sales", "SalesPass!2026", "SALES", actor_id=admin_id
    )
    database.create_user(
        "slip-inventory",
        "Slip Inventory",
        "InventoryPass!2026",
        "INVENTORY_MANAGER",
        actor_id=admin_id,
    )
    database.create_user(
        "slip-analyst",
        "Slip Analyst",
        "AnalystPass!2026",
        "REPORT_ANALYST",
        actor_id=admin_id,
    )
    database.set_actor(admin_id)
    customer_id = database.save_customer({
        "customer_code": "CUS-SLIP",
        "name": "Nguyễn An",
        "phone": "0900000000",
        "email": "an@example.test",
        "address": "Hà Nội",
        "note": "",
    })
    animal_id = database.save_animal({
        "animal_code": "PET-SLIP-PAID",
        "name": "Milo",
        "species": "Mèo",
        "breed": "Mèo ta",
        "gender": "Đực",
        "birth_date": "2025-01-10",
        "color": "Vàng",
        "weight": 3.5,
        "origin": "Trong nước",
        "purchase_price": 1_000_000,
        "sale_price": 2_000_000,
        "status": "AVAILABLE",
        "health_status": "Bình thường",
        "description": "",
    })
    order_id = database.create_sales_order({
        "order_code": "SO-SLIP-PAID",
        "customer_id": customer_id,
        "animal_ids": [animal_id],
        "ordered_at": "2026-01-02",
        "note": "",
    })
    database.add_payment(order_id, {
        "amount": 2_000_000,
        "method": "CASH",
        "paid_at": "2026-01-03",
        "reference": "",
        "note": "",
    })
    unpaid_animal_id = database.save_animal({
        "animal_code": "PET-SLIP-UNPAID",
        "name": "Luna",
        "species": "Mèo",
        "breed": "Mèo ta",
        "gender": "Cái",
        "birth_date": "2025-02-10",
        "color": "Xám",
        "weight": 3,
        "origin": "Trong nước",
        "purchase_price": 1_000_000,
        "sale_price": 1_500_000,
        "status": "AVAILABLE",
        "health_status": "Bình thường",
        "description": "",
    })
    unpaid_order_id = database.create_sales_order({
        "order_code": "SO-SLIP-UNPAID",
        "customer_id": customer_id,
        "animal_ids": [unpaid_animal_id],
        "ordered_at": "2026-01-02",
        "note": "",
    })
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path / "HTML", port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        anonymous = build_opener()
        type_url = f"{origin}/api/store/slip-types/ban-giao-don-da-thanh-toan"
        status, _, _ = _request(anonymous, type_url)
        assert status == 401

        analyst = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            analyst,
            f"{origin}/api/login",
            "POST",
            {"username": "slip-analyst", "password": "AnalystPass!2026"},
        )
        assert status == 200
        status, _, _ = _request(analyst, type_url)
        assert status == 403
        status, _, _ = _request(
            analyst,
            f"{origin}/api/store/slips",
            "POST",
            {"type": "ban-giao-don-da-thanh-toan", "payload": {}},
        )
        assert status == 403

        sales = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            sales,
            f"{origin}/api/login",
            "POST",
            {"username": "slip-sales", "password": "SalesPass!2026"},
        )
        assert status == 200
        status, _, payload = _request(sales, type_url)
        assert status == 200
        assert json.loads(payload)["type"]["title"] == "Bàn giao đơn khách đã thanh toán"

        paid_payload = {
            "issue_date": "2026-10-12",
            "reference": "SO-SLIP-PAID",
            "party": "Nguyễn An",
            "item_code": "PET-SLIP-PAID",
            "item_name": "Milo",
            "quantity": 1,
            "unit": "thú cưng",
            "reason": "Đơn đã thanh toán đủ.",
            "destination": "Hà Nội",
            "receiver": "Nguyễn An",
            "notes": "Test lưu phiếu",
        }
        status, _, payload = _request(
            sales,
            f"{origin}/api/store/slips",
            "POST",
            {
                "type": "ban-giao-don-da-thanh-toan",
                "linked_order_id": order_id,
                "payload": paid_payload,
            },
        )
        assert status == 201
        saved = json.loads(payload)["record"]
        assert saved["linked_order_id"] == order_id
        assert saved["payload"]["reference"] == "SO-SLIP-PAID"

        status, _, payload = _request(
            sales,
            f"{origin}/api/store/slips?type=ban-giao-don-da-thanh-toan",
        )
        assert status == 200
        assert json.loads(payload)["records"][0]["slip_code"] == saved["code"]
        status, _, payload = _request(sales, f"{origin}/api/store/slips/{saved['id']}")
        assert status == 200
        assert json.loads(payload)["record"]["payload"] == saved["payload"]

        status, _, _ = _request(
            sales,
            f"{origin}/api/store/slips",
            "POST",
            {
                "type": "ban-giao-don-da-thanh-toan",
                "linked_order_id": unpaid_order_id,
                "payload": paid_payload,
            },
        )
        assert status == 400
        status, _, _ = _request(
            sales,
            f"{origin}/api/store/slips",
            "POST",
            {
                "type": "ban-giao-don-da-thanh-toan",
                "linked_order_id": order_id,
                "payload": {**paid_payload, "unexpected": "value"},
            },
        )
        assert status == 400

        inventory = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            inventory,
            f"{origin}/api/login",
            "POST",
            {"username": "slip-inventory", "password": "InventoryPass!2026"},
        )
        assert status == 200
        status, _, payload = _request(
            inventory,
            f"{origin}/api/store/slips",
            "POST",
            {
                "type": "muon-hang-chup-anh",
                "payload": {
                    "issue_date": "2026-10-12",
                    "reference": "MEDIA-001",
                    "item_code": "FOOD-001",
                    "item_name": "Thức ăn mẫu",
                    "quantity": 2,
                    "unit": "gói",
                    "destination": "Phòng chụp",
                    "reason": "Cho mượn chụp ảnh sản phẩm.",
                    "receiver": "Nhân viên nội dung",
                },
            },
        )
        assert status == 201
        inventory_slip = json.loads(payload)["record"]
        status, _, _ = _request(
            sales, f"{origin}/api/store/slips/{inventory_slip['id']}"
        )
        assert status == 403
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
        {
            "customer_id": customer_two,
            "name": "Pet Two",
            "species": "Cat",
            "health_status": "Cần theo dõi",
            "body_condition": "Hơi thừa cân",
            "activity_level": "Thấp",
        }
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
        assert customer_two_portal["pets"][0]["health_status"] == "Cần theo dõi"
        assert customer_two_portal["pets"][0]["body_condition"] == "Hơi thừa cân"
        assert customer_two_portal["pets"][0]["activity_level"] == "Thấp"

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


def test_storefront_checkout_creates_unpaid_sale_and_fulfills_stock_atomically(
    tmp_path: Path,
):
    database_path = tmp_path / "storefront-requests.db"
    _create_admin_and_supplier(database_path)
    database = Database(database_path)
    with database.connection:
        database.connection.execute(
            """
            INSERT INTO inventory_items
                (item_code, name, category, unit, is_demo, retail_price, is_active)
            VALUES ('WEB-REQUEST-ITEM', 'Request item', 'SUPPLIES', 'cái', 1, 0, 1)
            """
        )
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        anonymous = build_opener()
        status, _, payload = _request(
            anonymous, f"{origin}/api/modules/module_12_orders/records"
        )
        assert status == 401

        request_body = {
            "name": "Nguyễn An",
            "phone": "0901-234-567",
            "address": "Quận 1",
            "note": "Xin cửa hàng tư vấn",
            "consent": True,
            "clientRequestId": "f457c6a1-f563-45d7-85c2-08d750eb4782",
            "items": [{"id": "WEB-REQUEST-ITEM", "quantity": 2}],
        }
        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            {**request_body, "consent": False},
        )
        assert status == 400

        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            request_body,
        )
        assert status == 400
        assert "chưa được xác minh" in json.loads(payload)["error"]

        database = Database(database_path)
        with database.connection:
            database.connection.execute(
                """
                UPDATE inventory_items SET is_demo = 0, retail_price = 100
                WHERE item_code = 'WEB-REQUEST-ITEM'
                """
            )
            item_id = database.connection.execute(
                "SELECT id FROM inventory_items WHERE item_code = 'WEB-REQUEST-ITEM'"
            ).fetchone()["id"]
            database.connection.execute(
                """
                INSERT INTO inventory_batches
                    (item_id, batch_code, quantity_remaining, unit_cost)
                VALUES (?, 'WEB-TEST-BATCH', 6, 30)
                """,
                (item_id,),
            )
        database.close()

        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            {
                **request_body,
                "items": [{"id": "WEB-REQUEST-ITEM", "quantity": 99}],
            },
        )
        assert status == 400
        database = Database(database_path)
        assert database.connection.execute(
            "SELECT COUNT(*) FROM sales_orders"
        ).fetchone()[0] == 0
        assert database.connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0] == 0
        assert database.connection.execute(
            "SELECT COUNT(*) FROM storefront_order_requests"
        ).fetchone()[0] == 0
        assert database.connection.execute(
            """
            SELECT quantity_remaining FROM inventory_batches
            WHERE batch_code = 'WEB-TEST-BATCH'
            """
        ).fetchone()["quantity_remaining"] == 6
        database.close()

        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            request_body,
        )
        assert status == 201
        confirmation = json.loads(payload)
        assert confirmation["requestCode"].startswith("BBR-")
        assert confirmation["status"] == "ORDER_CREATED"
        assert confirmation["salesOrderStatus"] == "OPEN"
        assert confirmation["inventoryFulfilled"] is True
        status, _, retry_payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            request_body,
        )
        assert status == 201
        assert json.loads(retry_payload)["requestCode"] == confirmation["requestCode"]
        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests",
            "POST",
            {**request_body, "phone": "0909-999-999"},
        )
        assert status == 400
        assert "đã được dùng cho yêu cầu khác" in json.loads(payload)["error"]

        status, _, payload = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests/{confirmation['requestCode']}",
        )
        assert status == 200
        lookup = json.loads(payload)
        assert lookup == {
            "requestCode": confirmation["requestCode"],
            "status": "NEW",
            "salesOrderCode": confirmation["salesOrderCode"],
            "salesOrderStatus": "OPEN",
            "salesOrderTotal": 200.0,
            "inventoryFulfilled": True,
        }
        status, _, _ = _request(
            anonymous,
            f"{origin}/api/storefront/order-requests/BBR-20990101-NOTREAL",
        )
        assert status == 404

        database = Database(database_path)
        assert database.connection.execute("SELECT COUNT(*) FROM sales_orders").fetchone()[0] == 1
        assert database.connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 1
        assert database.connection.execute(
            "SELECT status, inventory_fulfilled_at FROM sales_orders"
        ).fetchone()["status"] == "OPEN"
        batch = database.connection.execute(
            "SELECT quantity_remaining FROM inventory_batches WHERE batch_code = 'WEB-TEST-BATCH'"
        ).fetchone()
        assert batch["quantity_remaining"] == 4
        product = database.connection.execute(
            """
            SELECT is_active, storefront_auto_inactive
            FROM inventory_items WHERE item_code = 'WEB-REQUEST-ITEM'
            """
        ).fetchone()
        assert product["is_active"] == 0
        assert product["storefront_auto_inactive"] == 1
        assert database.connection.execute(
            "SELECT COUNT(*) FROM storefront_order_requests"
        ).fetchone()[0] == 1

        staff = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            staff,
            f"{origin}/api/login",
            "POST",
            {"username": "bridge-admin", "password": "StrongPass!2026"},
        )
        assert status == 200
        status, _, payload = _request(
            staff, f"{origin}/api/modules/module_12_orders/records"
        )
        assert status == 200
        records = json.loads(payload)["records"]
        request = next(
            row for row in records if row["record_type"] == "STOREFRONT_REQUEST"
        )
        assert request["request_code"] == confirmation["requestCode"]
        assert request["customer_name"] == "Nguyễn An"
        assert request["customer_phone"] == "0901-234-567"
        assert request["items"] == [{
            "item_code": "WEB-REQUEST-ITEM",
            "name": "Request item",
            "quantity": 2,
        }]
        assert request["sales_order_code"] == confirmation["salesOrderCode"]
        assert request["sales_order_status"] == "OPEN"
        database.cancel_sales_order(request["sales_order_id"])
        restored = database.connection.execute(
            """
            SELECT i.is_active, i.storefront_auto_inactive, b.quantity_remaining
            FROM inventory_items i
            JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.item_code = 'WEB-REQUEST-ITEM'
            """
        ).fetchone()
        assert restored["is_active"] == 1
        assert restored["storefront_auto_inactive"] == 0
        assert restored["quantity_remaining"] == 6

        paid_order = database.create_storefront_sales_order({
            "request_code": "BBR-20261013-PAYTEST",
            "client_request_id": "c158fa6c-8fc6-4264-a6a1-aa8a6adfb516",
            "customer_name": "Nguyễn An",
            "customer_phone": "0901-234-567",
            "items": [{
                "item_code": "WEB-REQUEST-ITEM",
                "name": "Request item",
                "quantity": 1,
            }],
        })
        assert paid_order["sales_order_status"] == "OPEN"
        assert database.connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0] == 1
        assert database.connection.execute(
            """
            SELECT quantity_remaining FROM inventory_batches
            WHERE batch_code = 'WEB-TEST-BATCH'
            """
        ).fetchone()["quantity_remaining"] == 5
        database.add_payment(
            paid_order["sales_order_id"],
            {
                "amount": 100,
                "method": "CASH",
                "paid_at": date.today().isoformat(),
            },
        )
        assert database.connection.execute(
            """
            SELECT status FROM sales_orders WHERE id = ?
            """,
            (paid_order["sales_order_id"],),
        ).fetchone()["status"] == "PAID"
        assert database.connection.execute(
            """
            SELECT quantity_remaining FROM inventory_batches
            WHERE batch_code = 'WEB-TEST-BATCH'
            """
        ).fetchone()["quantity_remaining"] == 5
        database.close()
    finally:
        bridge.stop()


def test_web_sales_actions_require_approval_and_manager_can_review(tmp_path: Path):
    database_path = tmp_path / "sales-approval-bridge.db"
    _create_admin_and_supplier(database_path)
    database = Database(database_path)
    manager_id = database.auth.create_user(
        "approval-manager",
        "Approval Manager",
        "ManagerPass!2026",
        "MANAGER",
    )
    sales_id = database.auth.create_user(
        "approval-sales",
        "Approval Sales",
        "SalesPass!2026",
        "SALES",
    )
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path, port=0)
    bridge.start()
    try:
        origin = bridge.base_url
        sales = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            sales,
            f"{origin}/api/login",
            "POST",
            {"username": "approval-sales", "password": "SalesPass!2026"},
        )
        assert status == 200

        status, _, response = _request(
            sales,
            f"{origin}/api/sales/actions",
            "POST",
            {
                "actionType": "save_customer",
                "payload": {
                    "values": {
                        "customer_code": "CUS-APPROVAL",
                        "name": "Approval Customer",
                        "phone": "0900000011",
                        "email": "",
                        "address": "",
                        "note": "",
                    }
                },
            },
        )
        assert status == 201
        request = json.loads(response)
        assert request["status"] == "PENDING"

        status, _, response = _request(
            sales, f"{origin}/api/sales/approval-requests"
        )
        assert status == 200
        listed = json.loads(response)["requests"]
        assert listed[0]["request_code"] == request["request_code"]
        assert listed[0]["payload"]["values"]["name"] == "Approval Customer"

        status, _, _ = _request(
            sales,
            f"{origin}/api/sales/approval-requests/{request['request_id']}/decision",
            "POST",
            {"decision": "approve"},
        )
        assert status == 403

        manager = build_opener(HTTPCookieProcessor(CookieJar()))
        status, _, _ = _request(
            manager,
            f"{origin}/api/login",
            "POST",
            {"username": "approval-manager", "password": "ManagerPass!2026"},
        )
        assert status == 200
        status, _, response = _request(
            manager,
            f"{origin}/api/sales/approval-requests/{request['request_id']}/decision",
            "POST",
            {"decision": "approve", "note": "Đã xác minh hồ sơ"},
        )
        assert status == 200
        assert json.loads(response)["status"] == "APPROVE"

        database = Database(database_path)
        assert database.connection.execute(
            "SELECT name FROM customers WHERE customer_code = 'CUS-APPROVAL'"
        ).fetchone()["name"] == "Approval Customer"
        assert database.connection.execute(
            "SELECT status FROM sales_approval_requests WHERE id = ?",
            (request["request_id"],),
        ).fetchone()["status"] == "APPROVED"
        database.close()
    finally:
        bridge.stop()
