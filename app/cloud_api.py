from __future__ import annotations

import base64
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from typing import Any
from uuid import UUID

import jwt
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.database import Database
from app.modules.auth.constants import ROLE_LABELS, ROLE_PERMISSIONS
from app.storefront_catalog import build_storefront_catalog


LOGGER = logging.getLogger("pet_store.cloud_api")
DATABASE_PATH = Path(
    os.environ.get("PETCARE_DATABASE_PATH", "/var/lib/petcare/pet_store.db")
)
JWT_SECRET = os.environ.get("PETCARE_JWT_SECRET", "")
TOKEN_MINUTES = int(os.environ.get("PETCARE_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_HOURS = int(os.environ.get("PETCARE_REFRESH_TOKEN_HOURS", "12"))
BOOTSTRAP_ADMIN_USERNAME = os.environ.get("PETCARE_BOOTSTRAP_ADMIN_USERNAME", "")
BOOTSTRAP_ADMIN_PASSWORD = os.environ.get("PETCARE_BOOTSTRAP_ADMIN_PASSWORD", "")
BOOTSTRAP_ADMIN_DISPLAY_NAME = os.environ.get(
    "PETCARE_BOOTSTRAP_ADMIN_DISPLAY_NAME", "Quản trị viên"
)
TRUSTED_HOSTS = [
    host.strip()
    for host in os.environ.get("PETCARE_TRUSTED_HOSTS", "").split(",")
    if host.strip()
]
WEB_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get("PETCARE_WEB_ORIGINS", "").split(",")
    if origin.strip()
]
LOGIN_WINDOW_SECONDS = 900
LOGIN_MAX_ATTEMPTS = 8
MAX_REQUEST_BYTES = 10 * 1024 * 1024
MAX_LOGIN_RATE_LIMIT_KEYS = 50_000

@asynccontextmanager
async def api_lifespan(_app: FastAPI):
    initialize_cloud_database()
    yield


app = FastAPI(
    title="PetCare Central API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=api_lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=WEB_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
if TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            request_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=400, content={"detail": "Invalid Content-Length."}
            )
        if request_size < 0 or request_size > MAX_REQUEST_BYTES:
            return JSONResponse(
                status_code=413, content={"detail": "Request body is too large."}
            )
    return await call_next(request)

if JWT_SECRET and len(JWT_SECRET.encode("utf-8")) < 32:
    raise RuntimeError("PETCARE_JWT_SECRET must contain at least 32 bytes.")
if TOKEN_MINUTES < 5 or TOKEN_MINUTES > 240:
    raise RuntimeError("PETCARE_TOKEN_MINUTES must be between 5 and 240.")
if REFRESH_TOKEN_HOURS < 1 or REFRESH_TOKEN_HOURS > 72:
    raise RuntimeError("PETCARE_REFRESH_TOKEN_HOURS must be between 1 and 72.")

_login_attempts: dict[str, deque[float]] = {}
_login_attempts_lock = threading.Lock()


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=1024)


class RpcBody(BaseModel):
    method: str = Field(min_length=1, max_length=120)
    args: list[Any] = Field(default_factory=list, max_length=32)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = Field(default=None, max_length=36)


class PermissionBody(BaseModel):
    permission: str = Field(min_length=1, max_length=100)


class ChangePasswordBody(BaseModel):
    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(min_length=12, max_length=1024)


class StorefrontOrderItem(BaseModel):
    model_config = {"extra": "forbid"}

    id: str = Field(min_length=1, max_length=100)
    quantity: int = Field(strict=True, ge=1, le=99)


class StorefrontOrderBody(BaseModel):
    model_config = {"extra": "forbid", "populate_by_name": True}

    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=30)
    address: str = Field(default="", max_length=240)
    note: str = Field(default="", max_length=500)
    consent: bool
    client_request_id: str = Field(
        alias="clientRequestId", min_length=36, max_length=36
    )
    items: list[StorefrontOrderItem] = Field(min_length=1, max_length=50)


def _database(*, initialize: bool = False) -> Database:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Central API is not configured.",
        )
    try:
        return Database(DATABASE_PATH, initialize=initialize)
    except (OSError, sqlite3.Error):
        LOGGER.exception("Could not open central PetCare database")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Central database is unavailable.",
        )


def _client_key(request: Request, username: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{username.strip().casefold()[:64]}"


def _check_login_rate(request: Request, username: str) -> None:
    now = time.monotonic()
    key = _client_key(request, username)
    with _login_attempts_lock:
        attempts = _login_attempts.get(key)
        if attempts is None:
            if len(_login_attempts) >= MAX_LOGIN_RATE_LIMIT_KEYS:
                _login_attempts.pop(next(iter(_login_attempts)))
            attempts = deque()
            _login_attempts[key] = attempts
        while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
            attempts.popleft()
        if len(attempts) >= LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later.",
            )
        attempts.append(now)


def _make_token(user: dict[str, Any]) -> str:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Central API is not configured.",
        )
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user["id"]),
            "iat": now,
            "exp": now + timedelta(minutes=TOKEN_MINUTES),
            "iss": "petcare-central",
            "token_use": "access",
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def _make_refresh_token(user: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user["id"]),
            "iat": now,
            "exp": now + timedelta(hours=REFRESH_TOKEN_HOURS),
            "iss": "petcare-central",
            "token_use": "refresh",
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def _decode_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode_value(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {"__bytes__"} and isinstance(value["__bytes__"], str):
            try:
                return base64.b64decode(value["__bytes__"], validate=True)
            except ValueError as error:
                raise HTTPException(400, "Malformed binary RPC argument.") from error
        return {key: _decode_value(item) for key, item in value.items()}
    return value


def _encode_value(value: Any) -> Any:
    if isinstance(value, sqlite3.Row):
        return {key: _encode_value(value[key]) for key in value.keys()}
    if isinstance(value, dict):
        return {str(key): _encode_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_encode_value(item) for item in value]
    if isinstance(value, bytes):
        return {"__bytes__": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Unsupported API result value: {type(value).__name__}")


def _build_rpc_permissions() -> dict[str, tuple[str, ...]]:
    permissions: dict[str, tuple[str, ...]] = {}

    def allow(permission: str, names: str) -> None:
        for name in names.split():
            permissions[name] = (permission,)

    allow(
        "dashboard.view",
        "dashboard_counts recent_animals",
    )
    allow(
        "animals.view",
        "list_animals get_animal get_intake_receipt list_vaccination_records "
        "list_vaccination_schedules list_disease_catalog",
    )
    allow(
        "store.view",
        "list_cages get_cage list_cage_animals list_cage_history",
    )
    allow(
        "imports.view",
        "list_suppliers get_supplier list_import_batches list_import_animals "
        "list_inspections",
    )
    allow("health.view", "list_health_records")
    allow("care.view", "list_care_tasks get_care_checklist")
    allow(
        "sales.view",
        "list_customers get_customer list_pets get_pet get_order_balance get_reservation_balance "
        "list_reservations list_saleable_animals list_sales_orders list_order_items "
        "list_order_product_items list_order_payments list_sales_approval_requests "
        "list_saleable_products list_saleable_combos",
    )
    allow("sales.view", "customers.list_pets customers.get_pet")
    allow(
        "membership.view",
        "list_membership_plans list_memberships list_membership_bills "
        "list_membership_bill_payments",
    )
    allow(
        "services.view",
        "list_service_packages list_service_staff list_service_appointments "
        "get_service_quote list_customer_service_memberships",
    )
    allow(
        "inventory.view",
        "list_inventory_items list_inventory_combos list_inventory_batches "
        "list_inventory_combo_items list_inventory_movements get_inventory_item expiring_inventory_batches "
        "low_stock_items get_feeding_recommendations list_feeding_age_rules "
        "list_animal_product_preferences",
    )
    allow(
        "inventory.view",
        "get_recommendation_profile list_recommendation_products "
        "list_recommendation_interactions list_recommendation_peer_interactions "
        "list_nutrition_foods_for_species",
    )
    allow("notifications.view", "list_operational_alerts notifications.get_alert_summary")
    allow("reports.view", "report_inventory report_sales report_health")
    allow("audit.view", "list_audit_events")
    allow("users.manage", "list_users user_count")
    allow("settings.manage", "get_setting")
    allow("settings.manage", "list_web_dataset_records")
    allow(
        "animals.manage",
        "save_animal delete_animal save_animal_product_preference "
        "delete_animal_product_preference",
    )
    allow(
        "store.manage",
        "save_cage delete_cage set_cage_active assign_animal_to_cage "
        "unassign_animal_from_cage",
    )
    allow(
        "imports.manage",
        "save_supplier set_supplier_active create_import_batch add_import_animal "
        "record_inspection",
    )
    allow(
        "health.manage",
        "add_health_record add_vaccination_record add_disease_catalog_entry",
    )
    allow(
        "care.manage",
        "add_care_task save_care_checklist set_care_task_completed",
    )
    allow("sales.manage", "save_customer create_reservation release_reservation")
    allow("sales.manage", "create_sales_order create_product_sales_order add_payment")
    allow("sales.manage", "cancel_sales_order refund_reservation_deposit")
    allow(
        "sales.manage",
        "approve_customer_portal_account reject_customer_portal_account "
        "list_customer_portal_accounts list_customer_portal_invites "
        "create_customer_portal_invite expire_customer_portal_invite",
    )
    allow(
        "inventory.view",
        "save_animal_product_preference delete_animal_product_preference "
        "record_recommendation_interaction",
    )
    allow(
        "membership.manage",
        "save_membership_plan create_membership create_membership_renewal "
        "add_membership_bill_payment",
    )
    allow(
        "services.manage",
        "create_service_appointment reschedule_service_appointment "
        "update_service_appointment_status",
    )
    allow("services.catalog.manage", "save_service_package")
    allow(
        "inventory.manage",
        "save_inventory_item set_inventory_item_active save_inventory_combo "
        "receive_inventory_stock consume_inventory_stock save_feeding_age_rule",
    )
    allow(
        "inventory.manage",
        "save_recommendation_profile delete_recommendation_profile",
    )
    allow("settings.manage", "save_setting import_web_dataset_records")
    allow("users.manage", "create_user set_user_role set_user_active set_sales_approver")
    allow("sales.fulfill", "create_store_slip list_store_slips get_store_slip")
    allow("sales.manage", "submit_sales_action")
    allow("sales.approve", "review_sales_approval_request")
    allow("dashboard.view", "current_actor_name")
    return permissions


RPC_PERMISSIONS = _build_rpc_permissions()


def _current_user(
    authorization: str | None,
    database: Database,
) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            issuer="petcare-central",
            options={"require": ["exp", "iat", "sub", "iss", "token_use"]},
        )
        if claims["token_use"] != "access":
            raise jwt.InvalidTokenError("Access token required.")
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from error
    user = database.connection.execute(
        """
        SELECT id, username, display_name, role, is_active, must_change_password
        FROM users WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    if user is None or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account is unavailable.")
    return dict(user)


def _resolve_method(database: Database, method_name: str) -> Any:
    target: Any = database
    for component in method_name.split("."):
        if not component or component.startswith("_"):
            raise HTTPException(status_code=403, detail="Method is not available.")
        target = getattr(target, component, None)
        if target is None:
            raise HTTPException(status_code=404, detail="Method is not available.")
    if not callable(target):
        raise HTTPException(status_code=403, detail="Method is not callable.")
    return target


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/storefront/catalog")
def storefront_catalog() -> dict[str, Any]:
    database = _database()
    try:
        return build_storefront_catalog(database.connection, source_type="central_api")
    except Exception:
        LOGGER.exception("Could not read central storefront catalog")
        raise HTTPException(
            status_code=500, detail="Could not read the product catalog."
        )
    finally:
        database.close()


@app.post("/api/storefront/order-requests", status_code=status.HTTP_201_CREATED)
def create_storefront_order(body: StorefrontOrderBody) -> dict[str, Any]:
    if body.consent is not True:
        raise HTTPException(
            status_code=400, detail="Cần đồng ý gửi thông tin đến cửa hàng."
        )
    if len(re.sub(r"\D", "", body.phone)) < 7:
        raise HTTPException(
            status_code=400, detail="Số điện thoại cần có ít nhất 7 chữ số."
        )
    if not body.name.strip() or not body.phone.strip():
        raise HTTPException(
            status_code=400, detail="Vui lòng nhập họ tên và số điện thoại."
        )
    item_codes = [item.id.strip() for item in body.items]
    if any(not item_code for item_code in item_codes):
        raise HTTPException(status_code=400, detail="Mã sản phẩm không hợp lệ.")
    if len(set(item_codes)) != len(item_codes):
        raise HTTPException(
            status_code=400,
            detail="Không được lặp sản phẩm trong yêu cầu.",
        )
    try:
        client_request_id = str(UUID(body.client_request_id))
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail="Mã gửi đơn không hợp lệ; hãy tải lại trang."
        ) from error

    database = _database()
    try:
        order = database.create_storefront_sales_order(
            {
                "request_code": (
                    f"BBR-{datetime.now(timezone.utc):%Y%m%d}-"
                    f"{secrets.token_hex(4).upper()}"
                ),
                "client_request_id": client_request_id,
                "customer_name": body.name.strip(),
                "customer_phone": body.phone.strip(),
                "address": body.address.strip(),
                "note": body.note.strip(),
                "items": [
                    {"item_code": item_code, "quantity": item.quantity}
                    for item_code, item in zip(item_codes, body.items, strict=True)
                ],
            }
        )
        return {
            "id": order["request_id"],
            "requestCode": order["request_code"],
            "status": "ORDER_CREATED",
            "salesOrderCode": order["sales_order_code"],
            "salesOrderStatus": order["sales_order_status"],
            "salesOrderTotal": order["sales_order_total"],
            "inventoryFulfilled": True,
            "message": "Đơn đã được tạo và xuất kho; đơn đang chờ thanh toán.",
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception:
        LOGGER.exception("Could not create central storefront order")
        raise HTTPException(
            status_code=500,
            detail="Không thể lưu yêu cầu. Vui lòng thử lại sau.",
        )
    finally:
        database.close()


@app.get("/api/storefront/order-requests/{request_code}")
def get_storefront_order(request_code: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Z0-9-]{1,40}", request_code):
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu.")
    database = _database()
    try:
        row = database.connection.execute(
            """
            SELECT r.request_code, r.status, so.order_code AS sales_order_code,
                   so.status AS sales_order_status,
                   so.total_amount AS sales_order_total,
                   so.inventory_fulfilled_at
            FROM storefront_order_requests r
            LEFT JOIN sales_orders so ON so.id = r.sales_order_id
            WHERE r.request_code = ?
            """,
            (request_code,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu.")
        return {
            "requestCode": row["request_code"],
            "status": row["status"],
            "salesOrderCode": row["sales_order_code"],
            "salesOrderStatus": row["sales_order_status"],
            "salesOrderTotal": row["sales_order_total"],
            "inventoryFulfilled": row["inventory_fulfilled_at"] is not None,
        }
    finally:
        database.close()


def initialize_cloud_database() -> None:
    if not JWT_SECRET or len(JWT_SECRET.encode("utf-8")) < 32:
        raise RuntimeError("Set PETCARE_JWT_SECRET to at least 32 bytes.")
    if bool(BOOTSTRAP_ADMIN_USERNAME) != bool(BOOTSTRAP_ADMIN_PASSWORD):
        raise RuntimeError(
            "Set both PETCARE_BOOTSTRAP_ADMIN_USERNAME and "
            "PETCARE_BOOTSTRAP_ADMIN_PASSWORD, or neither."
        )
    database = _database(initialize=True)
    try:
        with database.connection:
            database.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS api_rpc_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    method TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('RUNNING', 'SUCCEEDED', 'FAILED')
                    ),
                    result_json TEXT,
                    error_status INTEGER,
                    error_message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        if database.user_count() == 0:
            if not BOOTSTRAP_ADMIN_USERNAME:
                raise RuntimeError(
                    "An empty central database requires bootstrap admin credentials."
                )
            database.create_initial_admin(
                BOOTSTRAP_ADMIN_USERNAME,
                BOOTSTRAP_ADMIN_DISPLAY_NAME,
                BOOTSTRAP_ADMIN_PASSWORD,
            )
            LOGGER.warning(
                "Created the initial cloud administrator; rotate the bootstrap "
                "secret in the deployment environment."
            )
    finally:
        database.close()


@app.post("/api/auth/login")
def login(body: LoginBody, request: Request) -> dict[str, Any]:
    _check_login_rate(request, body.username)
    database = _database()
    try:
        user = database.authenticate(body.username, body.password)
        if user is None:
            database.record_audit(
                None,
                "LOGIN_FAILED",
                "user",
                details=f"cloud username={body.username[:64]}",
            )
            raise HTTPException(status_code=401, detail="Invalid username or password.")
        database.set_actor(int(user["id"]))
        database.record_audit(int(user["id"]), "CLOUD_LOGIN", "user", int(user["id"]))
        permissions = set(ROLE_PERMISSIONS.get(user["role"], ()))
        if database.has_permission(int(user["id"]), "sales.approve"):
            permissions.add("sales.approve")
        with _login_attempts_lock:
            _login_attempts.pop(_client_key(request, body.username), None)
        return {
            "access_token": _make_token(user),
            "refresh_token": _make_refresh_token(user),
            "token_type": "Bearer",
            "expires_in": TOKEN_MINUTES * 60,
            "user": {
                "id": int(user["id"]),
                "username": user["username"],
                "display_name": user["display_name"],
                "role": user["role"],
                "role_label": ROLE_LABELS.get(user["role"], user["role"]),
                "must_change_password": bool(user["must_change_password"]),
            },
            "permissions": sorted(permissions),
        }
    finally:
        database.close()


@app.post("/api/auth/refresh")
def refresh_access_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Refresh token required.")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            issuer="petcare-central",
            options={"require": ["exp", "iat", "sub", "iss", "token_use"]},
        )
        if claims["token_use"] != "refresh":
            raise jwt.InvalidTokenError("Refresh token required.")
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.") from error

    database = _database()
    try:
        user = database.connection.execute(
            """
            SELECT id, username, display_name, role, is_active, must_change_password
            FROM users WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        if user is None or not user["is_active"]:
            raise HTTPException(status_code=401, detail="Account is unavailable.")
        user_data = dict(user)
        permissions = set(ROLE_PERMISSIONS.get(user_data["role"], ()))
        if database.has_permission(user_id, "sales.approve"):
            permissions.add("sales.approve")
        return {
            "access_token": _make_token(user_data),
            "refresh_token": _make_refresh_token(user_data),
            "token_type": "Bearer",
            "expires_in": TOKEN_MINUTES * 60,
            "user": {
                "id": user_id,
                "username": user_data["username"],
                "display_name": user_data["display_name"],
                "role": user_data["role"],
                "role_label": ROLE_LABELS.get(
                    user_data["role"], user_data["role"]
                ),
                "must_change_password": bool(
                    user_data["must_change_password"]
                ),
            },
            "permissions": sorted(permissions),
        }
    finally:
        database.close()


@app.get("/api/auth/me")
def me(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    database = _database()
    try:
        user = _current_user(authorization, database)
        permissions = set(ROLE_PERMISSIONS.get(user["role"], ()))
        if database.has_permission(int(user["id"]), "sales.approve"):
            permissions.add("sales.approve")
        return {
            "user": {
                "id": int(user["id"]),
                "username": user["username"],
                "display_name": user["display_name"],
                "role": user["role"],
                "role_label": ROLE_LABELS.get(user["role"], user["role"]),
                "must_change_password": bool(user["must_change_password"]),
            },
            "permissions": sorted(permissions),
        }
    finally:
        database.close()


@app.post("/api/auth/permission")
def permission(
    body: PermissionBody,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, bool]:
    database = _database()
    try:
        user = _current_user(authorization, database)
        if user["must_change_password"]:
            raise HTTPException(403, "Change the temporary password first.")
        return {
            "granted": database.has_permission(int(user["id"]), body.permission)
        }
    finally:
        database.close()


@app.post("/api/auth/change-password")
def change_password(
    body: ChangePasswordBody,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, bool]:
    database = _database()
    try:
        user = _current_user(authorization, database)
        user_id = int(user["id"])
        database.set_actor(user_id)
        database.change_password(
            user_id, body.current_password, body.new_password, user_id
        )
        return {"changed": True}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        database.close()


@app.get("/api/rpc/requests/{request_id}")
def rpc_request_status(
    request_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    try:
        normalized_request_id = str(UUID(request_id))
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid request ID.") from error
    database = _database()
    try:
        user = _current_user(authorization, database)
        row = database.connection.execute(
            """
            SELECT status, result_json, error_status, error_message
            FROM api_rpc_requests WHERE request_id = ? AND user_id = ?
            """,
            (normalized_request_id, int(user["id"])),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Request not found.")
        return {
            "request_id": normalized_request_id,
            "status": row["status"],
            "result": (
                json.loads(row["result_json"])
                if row["result_json"] is not None
                else None
            ),
            "error_status": row["error_status"],
            "error_message": row["error_message"],
        }
    finally:
        database.close()


@app.post("/api/rpc")
def rpc(
    body: RpcBody,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    database = _database()
    try:
        user = _current_user(authorization, database)
        if user["must_change_password"]:
            raise HTTPException(403, "Change the temporary password first.")

        required = RPC_PERMISSIONS.get(body.method)
        if required is None:
            raise HTTPException(status_code=403, detail="Method is not available.")
        user_id = int(user["id"])
        if not any(database.has_permission(user_id, key) for key in required):
            if body.method == "submit_sales_action" and database.has_permission(
                user_id, "sales.request"
            ):
                pass
            else:
                raise HTTPException(status_code=403, detail="Insufficient permission.")

        database.set_actor(user_id)
        method = _resolve_method(database, body.method)
        args = _decode_value(body.args)
        kwargs = _decode_value(body.kwargs)

        request_id: str | None = None
        if body.request_id is not None:
            try:
                request_id = str(UUID(body.request_id))
            except ValueError as error:
                raise HTTPException(status_code=400, detail="Invalid request ID.") from error

        if request_id is not None:
            canonical_payload = json.dumps(
                {
                    "method": body.method,
                    "args": body.args,
                    "kwargs": body.kwargs,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            payload_hash = hashlib.sha256(
                canonical_payload.encode("utf-8")
            ).hexdigest()
            database.connection.execute("BEGIN IMMEDIATE")
            try:
                previous = database.connection.execute(
                    """
                    SELECT user_id, method, payload_hash, status, result_json,
                           error_status, error_message
                    FROM api_rpc_requests WHERE request_id = ?
                    """,
                    (request_id,),
                ).fetchone()
                if previous is not None:
                    database.connection.commit()
                    if (
                        int(previous["user_id"]) != user_id
                        or previous["method"] != body.method
                        or previous["payload_hash"] != payload_hash
                    ):
                        raise HTTPException(
                            status_code=409,
                            detail="Request ID was already used for another operation.",
                        )
                    if previous["status"] == "SUCCEEDED":
                        return {"result": json.loads(previous["result_json"])}
                    if previous["status"] == "FAILED":
                        raise HTTPException(
                            status_code=int(previous["error_status"] or 500),
                            detail=previous["error_message"]
                            or "The operation previously failed.",
                        )
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "This operation is still being processed. "
                            "Check its request status before continuing."
                        ),
                    )
                database.connection.execute(
                    """
                    INSERT INTO api_rpc_requests
                        (request_id, user_id, method, payload_hash, status)
                    VALUES (?, ?, ?, ?, 'RUNNING')
                    """,
                    (request_id, user_id, body.method, payload_hash),
                )
                database.connection.commit()
            except BaseException:
                if database.connection.in_transaction:
                    database.connection.rollback()
                raise

        try:
            result = method(*args, **kwargs)
            encoded_result = _encode_value(result)
            if request_id is not None:
                with database.connection:
                    database.connection.execute(
                        """
                        UPDATE api_rpc_requests
                        SET status = 'SUCCEEDED', result_json = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE request_id = ? AND user_id = ?
                        """,
                        (
                            json.dumps(
                                encoded_result,
                                ensure_ascii=False,
                                allow_nan=False,
                            ),
                            request_id,
                            user_id,
                        ),
                    )
            return {"result": encoded_result}
        except PermissionError as error:
            error_response = HTTPException(status_code=403, detail=str(error))
        except ValueError as error:
            error_response = HTTPException(status_code=400, detail=str(error))
        except sqlite3.IntegrityError as error:
            error_response = HTTPException(status_code=409, detail=str(error))
        except HTTPException as error:
            error_response = error
        except Exception:
            LOGGER.exception("Cloud RPC failed: method=%s", body.method)
            error_response = HTTPException(
                status_code=500, detail="The requested operation failed."
            )
        if request_id is not None:
            with database.connection:
                database.connection.execute(
                    """
                    UPDATE api_rpc_requests
                    SET status = 'FAILED', error_status = ?, error_message = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE request_id = ? AND user_id = ?
                    """,
                    (
                        error_response.status_code,
                        str(error_response.detail)[:500],
                        request_id,
                        user_id,
                    ),
                )
        raise error_response
    except HTTPException:
        raise
    except Exception:
        LOGGER.exception("Cloud RPC failed: method=%s", body.method)
        raise HTTPException(status_code=500, detail="The requested operation failed.")
    finally:
        database.close()
