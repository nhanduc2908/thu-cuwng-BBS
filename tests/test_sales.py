import sqlite3

import pytest

from app.database import Database


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "sales.db")
    yield instance
    instance.close()


def create_customer(database):
    return database.save_customer(
        {
            "customer_code": "CUS-001",
            "name": "Nguyễn An",
            "phone": "0900000000",
            "email": "",
            "address": "",
            "note": "",
        }
    )


def create_animal(database, code="PET-001", price=2_000_000):
    return database.save_animal(
        {
            "animal_code": code,
            "name": "Milo",
            "species": "Mèo",
            "breed": "Mèo ta",
            "gender": "Đực",
            "birth_date": "2025-01-10",
            "color": "Vàng",
            "weight": 3.5,
            "origin": "Trong nước",
            "purchase_price": 1_000_000,
            "sale_price": price,
            "status": "AVAILABLE",
            "health_status": "Bình thường",
            "description": "",
        }
    )


def reservation_values(customer_id, animal_id, deposit=0):
    return {
        "customer_id": customer_id,
        "animal_id": animal_id,
        "reserved_at": "2026-01-01",
        "expires_at": "2026-01-10",
        "deposit": deposit,
        "deposit_method": "CASH",
        "deposit_reference": "",
        "note": "",
    }


def order_values(customer_id, animal_ids, code="SO-001"):
    return {
        "order_code": code,
        "customer_id": customer_id,
        "animal_ids": animal_ids,
        "ordered_at": "2026-01-02",
        "note": "",
    }


def test_customer_reservation_deposit_refund_and_release(database):
    customer_id = create_customer(database)
    animal_id = create_animal(database)

    reservation_id = database.create_reservation(
        reservation_values(customer_id, animal_id, 500_000)
    )
    assert database.get_animal(animal_id)["status"] == "RESERVED"
    assert database.get_reservation_balance(reservation_id) == 500_000

    with pytest.raises(ValueError, match="hoàn đủ tiền cọc"):
        database.release_reservation(reservation_id)
    with pytest.raises(ValueError, match="vượt quá cọc"):
        database.refund_reservation_deposit(
            reservation_id,
            {
                "amount": 500_001,
                "method": "CASH",
                "refunded_at": "2026-01-03",
            },
        )

    database.refund_reservation_deposit(
        reservation_id,
        {
            "amount": 500_000,
            "method": "CASH",
            "refunded_at": "2026-01-03",
        },
    )
    database.release_reservation(reservation_id)
    assert database.get_animal(animal_id)["status"] == "AVAILABLE"
    assert database.list_reservations()[0]["status"] == "RELEASED"


def test_reserved_animal_deposit_converts_to_payment_and_full_payment_sells(
    database,
):
    customer_id = create_customer(database)
    animal_id = create_animal(database)
    database.create_reservation(reservation_values(customer_id, animal_id, 500_000))

    order_id = database.create_sales_order(
        order_values(customer_id, [animal_id])
    )
    order = database.list_sales_orders()[0]
    assert order["status"] == "PARTIALLY_PAID"
    assert order["paid_amount"] == 500_000
    assert database.list_reservations()[0]["status"] == "CONVERTED"

    with pytest.raises(ValueError, match="vượt quá công nợ"):
        database.add_payment(
            order_id,
            {
                "amount": 1_500_001,
                "method": "CASH",
                "paid_at": "2026-01-03",
            },
        )
    database.add_payment(
        order_id,
        {
            "amount": 1_500_000,
            "method": "BANK_TRANSFER",
            "paid_at": "2026-01-03",
        },
    )
    assert database.list_sales_orders()[0]["status"] == "PAID"
    assert database.get_animal(animal_id)["status"] == "SOLD"
    assert database.get_order_balance(order_id) == 0


def test_unpaid_order_can_be_cancelled_and_duplicate_code_rejected(database):
    customer_id = create_customer(database)
    animal_id = create_animal(database)
    order_id = database.create_sales_order(order_values(customer_id, [animal_id]))
    database.cancel_sales_order(order_id)
    assert database.get_animal(animal_id)["status"] == "AVAILABLE"

    another_animal_id = create_animal(database, "PET-002")
    with pytest.raises(sqlite3.IntegrityError):
        database.create_sales_order(
            order_values(customer_id, [another_animal_id], code="SO-001")
        )


def test_zero_price_order_is_completed_without_getting_stuck(database):
    customer_id = create_customer(database)
    animal_id = create_animal(database, price=0)
    database.create_sales_order(order_values(customer_id, [animal_id]))

    assert database.list_sales_orders()[0]["status"] == "PAID"
    assert database.get_animal(animal_id)["status"] == "SOLD"


def test_blank_order_code_is_rejected(database):
    customer_id = create_customer(database)
    animal_id = create_animal(database)

    with pytest.raises(ValueError, match="Mã đơn hàng"):
        database.create_sales_order(order_values(customer_id, [animal_id], code=" "))


def test_order_creation_rolls_back_all_animals_on_invalid_item(database):
    customer_id = create_customer(database)
    animal_id = create_animal(database)

    with pytest.raises(ValueError, match="Không tìm thấy động vật"):
        database.create_sales_order(
            order_values(customer_id, [animal_id, 999_999])
        )

    assert database.get_animal(animal_id)["status"] == "AVAILABLE"
    assert database.list_sales_orders() == []


def test_lower_sales_roles_submit_for_manager_approval_and_cannot_self_approve(
    database,
):
    admin_id = database.create_initial_admin(
        "admin", "Administrator", "AdminPass!2026"
    )
    database.set_actor(admin_id)
    manager_id = database.auth.create_user(
        "manager", "Manager", "ManagerPass!2026", "MANAGER"
    )
    sales_id = database.auth.create_user(
        "sales", "Sales Associate", "SalesPass!2026", "SALES"
    )
    customer_id = create_customer(database)
    animal_id = create_animal(database)
    order_id = database.create_sales_order(order_values(customer_id, [animal_id]))

    assert database.has_permission(sales_id, "sales.request")
    assert not database.has_permission(sales_id, "sales.manage")
    database.set_actor(sales_id)
    with pytest.raises(PermissionError):
        database.add_payment(
            order_id,
            {
                "amount": 2_000_000,
                "method": "CASH",
                "paid_at": "2026-01-03",
            },
        )

    submitted = database.submit_sales_action(
        "add_payment",
        {
            "order_id": order_id,
            "values": {
                "amount": 2_000_000,
                "method": "CASH",
                "paid_at": "2026-01-03",
            },
        },
    )
    assert submitted["status"] == "PENDING"
    assert database.get_order_balance(order_id) == 2_000_000
    with pytest.raises(PermissionError, match="sales.approve"):
        database.review_sales_approval_request(submitted["request_id"], True)

    database.set_actor(manager_id)
    database.review_sales_approval_request(submitted["request_id"], True)
    assert database.get_order_balance(order_id) == 0
    assert database.list_sales_approval_requests()[0]["status"] == "APPROVED"


def test_low_roles_cancel_only_up_to_fifteen_million_without_approval(database):
    admin_id = database.create_initial_admin(
        "admin", "Administrator", "AdminPass!2026"
    )
    database.set_actor(admin_id)
    manager_id = database.auth.create_user(
        "manager", "Manager", "ManagerPass!2026", "MANAGER"
    )
    support_id = database.auth.create_user(
        "support", "Customer Support", "SupportPass!2026", "CUSTOMER_SUPPORT"
    )
    customer_id = create_customer(database)
    small_animal_id = create_animal(database, "PET-SMALL", price=15_000_000)
    large_animal_id = create_animal(database, "PET-LARGE", price=15_000_001)
    small_order_id = database.create_sales_order(
        order_values(customer_id, [small_animal_id], "SO-SMALL")
    )
    large_order_id = database.create_sales_order(
        order_values(customer_id, [large_animal_id], "SO-LARGE")
    )

    database.set_actor(support_id)
    small_result = database.submit_sales_action(
        "cancel_sales_order", {"order_id": small_order_id}
    )
    assert small_result["status"] == "APPLIED"
    assert database.connection.execute(
        "SELECT status FROM sales_orders WHERE id = ?", (small_order_id,)
    ).fetchone()["status"] == "CANCELLED"

    large_result = database.submit_sales_action(
        "cancel_sales_order", {"order_id": large_order_id}
    )
    assert large_result["status"] == "PENDING"
    assert database.connection.execute(
        "SELECT status FROM sales_orders WHERE id = ?", (large_order_id,)
    ).fetchone()["status"] == "OPEN"

    database.set_actor(manager_id)
    database.review_sales_approval_request(large_result["request_id"], True)
    assert database.connection.execute(
        "SELECT status FROM sales_orders WHERE id = ?", (large_order_id,)
    ).fetchone()["status"] == "CANCELLED"


def test_designated_sales_lead_can_approve_but_not_self_approve(database):
    admin_id = database.create_initial_admin(
        "admin", "Administrator", "AdminPass!2026"
    )
    database.set_actor(admin_id)
    lead_id = database.auth.create_user(
        "lead", "Sales Lead", "LeadPass!2026", "SALES"
    )
    requester_id = database.auth.create_user(
        "requester", "Sales Associate", "SalesPass!2026", "SALES"
    )
    customer_id = create_customer(database)
    animal_id = create_animal(database)
    order_id = database.create_sales_order(order_values(customer_id, [animal_id]))
    database.set_sales_approver(lead_id, True, admin_id)
    assert database.has_permission(lead_id, "sales.approve")

    database.set_actor(requester_id)
    request = database.submit_sales_action(
        "add_payment",
        {
            "order_id": order_id,
            "values": {
                "amount": 2_000_000,
                "method": "CASH",
                "paid_at": "2026-01-03",
            },
        },
    )
    database.set_actor(lead_id)
    database.review_sales_approval_request(request["request_id"], True)
    assert database.get_order_balance(order_id) == 0

    self_request = database.submit_sales_action(
        "save_customer",
        {
            "values": {
                "customer_code": "CUS-SELF",
                "name": "Self request",
                "phone": "0911111111",
                "email": "",
                "address": "",
                "note": "",
            }
        },
    )
    with pytest.raises(ValueError, match="Không thể tự duyệt"):
        database.review_sales_approval_request(self_request["request_id"], True)


def test_refunds_at_fifteen_million_are_direct_but_larger_refunds_need_approval(
    database,
):
    admin_id = database.create_initial_admin(
        "admin", "Administrator", "AdminPass!2026"
    )
    database.set_actor(admin_id)
    manager_id = database.auth.create_user(
        "manager", "Manager", "ManagerPass!2026", "MANAGER"
    )
    support_id = database.auth.create_user(
        "support", "Customer Support", "SupportPass!2026", "CUSTOMER_SUPPORT"
    )
    customer_id = create_customer(database)
    low_animal_id = create_animal(database, "PET-REFUND-LOW", price=20_000_000)
    high_animal_id = create_animal(database, "PET-REFUND-HIGH", price=20_000_000)
    low_reservation = database.create_reservation(
        reservation_values(customer_id, low_animal_id, 15_000_000)
    )
    high_reservation = database.create_reservation(
        reservation_values(customer_id, high_animal_id, 15_000_001)
    )

    database.set_actor(support_id)
    direct = database.submit_sales_action(
        "refund_reservation_deposit",
        {
            "reservation_id": low_reservation,
            "values": {
                "amount": 15_000_000,
                "method": "CASH",
                "refunded_at": "2026-10-13",
            },
        },
    )
    assert direct["status"] == "APPLIED"
    assert database.get_reservation_balance(low_reservation) == 0

    pending = database.submit_sales_action(
        "refund_reservation_deposit",
        {
            "reservation_id": high_reservation,
            "values": {
                "amount": 15_000_001,
                "method": "BANK_TRANSFER",
                "refunded_at": "2026-10-13",
            },
        },
    )
    assert pending["status"] == "PENDING"
    assert database.get_reservation_balance(high_reservation) == 15_000_001
    database.set_actor(manager_id)
    database.review_sales_approval_request(pending["request_id"], True)
    assert database.get_reservation_balance(high_reservation) == 0
