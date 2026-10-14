from app.database import Database
from app.modules.auth.constants import ROLE_PERMISSIONS
from app.web_bridge import LocalAdminBridge


def test_sales_request_permissions_are_narrowly_scoped_by_role():
    request_roles = {
        "SALES",
        "CUSTOMER_SUPPORT",
        "CAREGIVER",
        "SERVICE_COORDINATOR",
        "INVENTORY_MANAGER",
    }
    for role in request_roles:
        permissions = ROLE_PERMISSIONS[role]
        assert {"sales.view", "sales.request"} <= permissions
        assert "sales.manage" not in permissions
    assert {"sales.manage", "sales.approve"} <= ROLE_PERMISSIONS["MANAGER"]
    assert "sales.fulfill" in ROLE_PERMISSIONS["SALES"]


def test_default_role_accounts_are_seeded_once_without_resetting_passwords(tmp_path):
    database = Database(tmp_path / "accounts.db")
    try:
        created, conflicts = database.seed_default_role_accounts()

        assert len(created) == 10
        assert conflicts == []
        accounts = (
            ("admin", "admin", "ADMIN", True),
            ("manager", "ManagerPass!2026", "MANAGER", False),
            ("veterinarian", "VetPass!2026", "VETERINARIAN", False),
            ("caregiver", "CaregiverPass!2026", "CAREGIVER", False),
            ("sales", "SalesPass!2026", "SALES", False),
            ("inventory_manager", "InventoryPass!2026", "INVENTORY_MANAGER", False),
            ("service_coordinator", "ServicePass!2026", "SERVICE_COORDINATOR", False),
            ("customer_support", "SupportPass!2026", "CUSTOMER_SUPPORT", False),
            ("report_analyst", "ReportPass!2026", "REPORT_ANALYST", False),
            ("auditor", "AuditorPass!2026", "AUDITOR", False),
        )
        for username, password, role, must_change in accounts:
            user = database.authenticate(username, password)
            assert user is not None
            assert user["role"] == role
            assert user["must_change_password"] is must_change

        manager = database.authenticate("manager", "ManagerPass!2026")
        database.change_password(
            int(manager["id"]),
            "ManagerPass!2026",
            "ManagerUpdated!2026",
        )
        assert database.seed_default_role_accounts() == ([], [])
        assert database.authenticate("manager", "ManagerUpdated!2026") is not None
        assert database.authenticate("manager", "ManagerPass!2026") is None
    finally:
        database.close()


def test_seed_preserves_existing_username_with_conflicting_role(tmp_path):
    database = Database(tmp_path / "conflicting-accounts.db")
    try:
        database.auth.create_user(
            "manager", "Existing sales account", "ExistingPass!2026", "SALES"
        )

        created, conflicts = database.seed_default_role_accounts()

        assert "manager" in conflicts
        assert len(created) == 9
        existing = database.authenticate("manager", "ExistingPass!2026")
        assert existing is not None
        assert existing["role"] == "SALES"
        assert database.authenticate("manager", "ManagerPass!2026") is None
    finally:
        database.close()


def test_html_bridge_uses_shared_accounts_and_requires_admin_password_rotation(
    tmp_path,
):
    database_path = tmp_path / "shared-accounts.db"
    database = Database(database_path)
    database.seed_default_role_accounts()
    database.close()

    bridge = LocalAdminBridge(database_path, tmp_path, port=0)
    bridge.start()
    try:
        from http.cookiejar import CookieJar
        import json
        from urllib.error import HTTPError
        from urllib.request import HTTPCookieProcessor, Request, build_opener

        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        origin = bridge.base_url

        def post_login(username, password):
            body = json.dumps(
                {"username": username, "password": password}
            ).encode()
            request = Request(
                f"{origin}/api/login",
                data=body,
                headers={
                    "Origin": origin,
                    "Content-Type": "application/json",
                    "X-PetCare-Request": "1",
                },
                method="POST",
            )
            try:
                response = opener.open(request, timeout=5)
            except HTTPError as error:
                return error.code, json.loads(error.read())
            return response.status, json.loads(response.read())

        status, response = post_login("manager", "ManagerPass!2026")
        assert status == 200
        assert response["authenticated"] is True

        request = Request(f"{origin}/api/logout", data=b"{}", headers={
            "Origin": origin,
            "Content-Type": "application/json",
            "X-PetCare-Request": "1",
        }, method="POST")
        opener.open(request, timeout=5).close()

        status, response = post_login("admin", "admin")
        assert status == 403
        assert "desktop" in response["error"]
    finally:
        bridge.stop()
