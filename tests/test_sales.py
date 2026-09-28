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
