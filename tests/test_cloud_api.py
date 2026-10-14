from uuid import uuid4

from fastapi.testclient import TestClient

from app import cloud_api
from app.database import Database


def test_central_api_cors_uses_an_explicit_non_credentialed_origin_allowlist() -> None:
    cors = next(
        middleware
        for middleware in cloud_api.app.user_middleware
        if middleware.cls is cloud_api.CORSMiddleware
    )
    assert cors.kwargs["allow_origins"] == cloud_api.WEB_ORIGINS
    assert "*" not in cors.kwargs["allow_origins"]
    assert cors.kwargs["allow_credentials"] is False
    assert cors.kwargs["allow_methods"] == ["GET", "POST"]


def test_public_storefront_uses_central_catalog_and_idempotent_order_flow(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        cloud_api, "DATABASE_PATH", tmp_path / "central" / "petcare.db"
    )
    monkeypatch.setattr(cloud_api, "JWT_SECRET", "test-secret-that-is-at-least-32-bytes")
    monkeypatch.setattr(cloud_api, "BOOTSTRAP_ADMIN_USERNAME", "cloud-admin")
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_PASSWORD", "CloudAdmin!Password42"
    )
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_DISPLAY_NAME", "Cloud Administrator"
    )

    with TestClient(cloud_api.app) as client:
        database = Database(cloud_api.DATABASE_PATH)
        try:
            admin = database.authenticate(
                "cloud-admin", "CloudAdmin!Password42"
            )
            assert admin is not None
            database.set_actor(int(admin["id"]))
            item_id = database.save_inventory_item(
                {
                    "item_code": "CENTRAL-WEB-001",
                    "name": "Central Web Product",
                    "category": "FOOD",
                    "unit": "bag",
                    "catalog_category": "Food",
                    "retail_price": 25_000,
                    "is_demo": False,
                }
            )
            database.receive_inventory_stock(
                item_id,
                {
                    "batch_code": "CENTRAL-WEB-BATCH-001",
                    "quantity": 10,
                    "unit_cost": 12_000,
                },
            )
        finally:
            database.close()

        catalog = client.get("/api/storefront/catalog")
        assert catalog.status_code == 200
        assert catalog.json()["sourceType"] == "central_api"
        assert any(
            product["item_code"] == "CENTRAL-WEB-001"
            for product in catalog.json()["products"]
        )

        request_id = str(uuid4())
        order_body = {
            "name": "Storefront Customer",
            "phone": "+84 912 345 678",
            "address": "Central API address",
            "note": "Please call first",
            "consent": True,
            "clientRequestId": request_id,
            "items": [{"id": "CENTRAL-WEB-001", "quantity": 1}],
        }
        created = client.post(
            "/api/storefront/order-requests", json=order_body
        )
        replayed = client.post(
            "/api/storefront/order-requests", json=order_body
        )
        assert created.status_code == 201
        assert replayed.status_code == 201
        assert replayed.json()["requestCode"] == created.json()["requestCode"]
        assert created.json()["salesOrderStatus"] == "OPEN"
        assert created.json()["inventoryFulfilled"] is True

        lookup = client.get(
            f"/api/storefront/order-requests/{created.json()['requestCode']}"
        )
        assert lookup.status_code == 200
        assert lookup.json()["salesOrderCode"] == created.json()["salesOrderCode"]
        assert lookup.json()["inventoryFulfilled"] is True
        assert "customer_name" not in lookup.json()
        assert "customer_phone" not in lookup.json()

        rejected = client.post(
            "/api/storefront/order-requests",
            json={**order_body, "consent": False, "clientRequestId": str(uuid4())},
        )
        assert rejected.status_code == 400

        database = Database(cloud_api.DATABASE_PATH)
        try:
            remaining = database.connection.execute(
                "SELECT quantity_remaining FROM inventory_batches WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            request_count = database.connection.execute(
                "SELECT COUNT(*) FROM storefront_order_requests"
            ).fetchone()[0]
            order_count = database.connection.execute(
                "SELECT COUNT(*) FROM sales_orders"
            ).fetchone()[0]
            assert remaining["quantity_remaining"] == 9
            assert request_count == 1
            assert order_count == 1
        finally:
            database.close()


def test_cloud_login_and_rpc_enforce_authenticated_method_permissions(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        cloud_api, "DATABASE_PATH", tmp_path / "central" / "petcare.db"
    )
    monkeypatch.setattr(cloud_api, "JWT_SECRET", "test-secret-that-is-at-least-32-bytes")
    monkeypatch.setattr(cloud_api, "BOOTSTRAP_ADMIN_USERNAME", "cloud-admin")
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_PASSWORD", "CloudAdmin!Password42"
    )
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_DISPLAY_NAME", "Cloud Administrator"
    )

    with TestClient(cloud_api.app) as client:
        login = client.post(
            "/api/auth/login",
            json={
                "username": "cloud-admin",
                "password": "CloudAdmin!Password42",
            },
        )
        assert login.status_code == 200
        admin_token = login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        assert client.get("/api/auth/me", headers=admin_headers).status_code == 200
        refreshed = client.post(
            "/api/auth/refresh",
            headers={
                "Authorization": f"Bearer {login.json()['refresh_token']}"
            },
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["user"]["role"] == "ADMIN"
        assert (
            client.get(
                "/api/auth/me",
                headers={
                    "Authorization": f"Bearer {login.json()['refresh_token']}"
                },
            ).status_code
            == 401
        )
        assert (
            client.post(
                "/api/rpc",
                headers=admin_headers,
                json={"method": "dashboard_counts"},
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/rpc",
                headers=admin_headers,
                json={"method": "connection.execute", "args": ["SELECT 1"]},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/rpc",
                headers=admin_headers,
                json={"method": "backup_to", "args": ["outside.db"]},
            ).status_code
            == 403
        )

        database = Database(cloud_api.DATABASE_PATH)
        try:
            admin = database.authenticate(
                "cloud-admin", "CloudAdmin!Password42"
            )
            assert admin is not None
            admin_id = int(admin["id"])
            database.set_actor(admin_id)
            database.create_user(
                "report-analyst",
                "Report Analyst",
                "Analyst!Password42",
                "REPORT_ANALYST",
                admin_id,
            )
        finally:
            database.close()

        analyst_login = client.post(
            "/api/auth/login",
            json={
                "username": "report-analyst",
                "password": "Analyst!Password42",
            },
        )
        assert analyst_login.status_code == 200
        analyst_headers = {
            "Authorization": f"Bearer {analyst_login.json()['access_token']}"
        }
        assert (
            client.post(
                "/api/rpc",
                headers=analyst_headers,
                json={"method": "list_users"},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/rpc",
                headers=analyst_headers,
                json={"method": "list_operational_alerts"},
            ).status_code
            == 403
        )


def test_rpc_request_id_replays_results_rejects_payload_reuse_and_reports_status(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        cloud_api, "DATABASE_PATH", tmp_path / "central" / "petcare.db"
    )
    monkeypatch.setattr(cloud_api, "JWT_SECRET", "test-secret-that-is-at-least-32-bytes")
    monkeypatch.setattr(cloud_api, "BOOTSTRAP_ADMIN_USERNAME", "cloud-admin")
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_PASSWORD", "CloudAdmin!Password42"
    )
    monkeypatch.setattr(
        cloud_api, "BOOTSTRAP_ADMIN_DISPLAY_NAME", "Cloud Administrator"
    )

    with TestClient(cloud_api.app) as client:
        login = client.post(
            "/api/auth/login",
            json={
                "username": "cloud-admin",
                "password": "CloudAdmin!Password42",
            },
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        request_id = str(uuid4())
        payload = {
            "method": "save_setting",
            "args": ["mobile_idempotency_test", "original"],
            "request_id": request_id,
        }

        first = client.post("/api/rpc", headers=headers, json=payload)
        replay = client.post("/api/rpc", headers=headers, json=payload)

        assert first.status_code == 200
        assert replay.status_code == 200
        assert replay.json() == first.json()
        setting = client.post(
            "/api/rpc",
            headers=headers,
            json={"method": "get_setting", "args": ["mobile_idempotency_test"]},
        )
        assert setting.json()["result"] == "original"

        reused_id = client.post(
            "/api/rpc",
            headers=headers,
            json={
                **payload,
                "args": ["mobile_idempotency_test", "changed"],
            },
        )
        assert reused_id.status_code == 409
        status = client.get(f"/api/rpc/requests/{request_id}", headers=headers)
        assert status.status_code == 200
        assert status.json()["status"] == "SUCCEEDED"

        failed_request_id = str(uuid4())
        failed = client.post(
            "/api/rpc",
            headers=headers,
            json={
                "method": "submit_sales_action",
                "args": ["unsupported-action", {}],
                "request_id": failed_request_id,
            },
        )
        assert failed.status_code == 400
        failure_status = client.get(
            f"/api/rpc/requests/{failed_request_id}", headers=headers
        )
        assert failure_status.status_code == 200
        assert failure_status.json()["status"] == "FAILED"
        assert failure_status.json()["error_status"] == 400

        database = Database(cloud_api.DATABASE_PATH)
        try:
            database.connection.execute(
                """
                UPDATE api_rpc_requests
                SET status = 'RUNNING', error_status = NULL, error_message = NULL
                WHERE request_id = ?
                """,
                (failed_request_id,),
            )
            database.connection.commit()
        finally:
            database.close()
        running = client.post(
            "/api/rpc",
            headers=headers,
            json={
                "method": "submit_sales_action",
                "args": ["unsupported-action", {}],
                "request_id": failed_request_id,
            },
        )
        assert running.status_code == 409
        running_status = client.get(
            f"/api/rpc/requests/{failed_request_id}", headers=headers
        )
        assert running_status.json()["status"] == "RUNNING"
