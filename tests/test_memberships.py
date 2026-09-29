from datetime import date, timedelta

import pytest

from app.database import Database


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "memberships.db")
    yield instance
    instance.close()


def create_customer(database):
    return database.save_customer(
        {
            "customer_code": "CUS-MEMBER-001",
            "name": "Nguyễn An",
            "phone": "0900000000",
        }
    )


def create_plan(database, price=1_000_000, duration=30):
    return database.save_membership_plan(
        {
            "code": "GOLD",
            "name": "Gold",
            "duration_days": duration,
            "price": price,
            "discount_percent": 5,
            "points_rate": 1,
            "max_pets": 2,
            "benefits": "Ưu đãi thành viên",
        }
    )


def payment(amount):
    return {
        "amount": amount,
        "method": "BANK_TRANSFER",
        "paid_at": date.today().isoformat(),
        "reference": "BANK-001",
    }


def test_membership_activates_only_after_full_payment(database):
    customer_id = create_customer(database)
    plan_id = create_plan(database)
    membership_id = database.create_membership(customer_id, plan_id)

    membership = next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )
    assert membership["display_status"] == "PENDING_PAYMENT"
    bill = database.list_membership_bills()[0]
    assert bill["status"] == "PENDING"
    assert bill["total_amount"] == 1_000_000

    database.add_membership_bill_payment(bill["id"], payment(400_000))
    assert database.list_membership_bills()[0]["status"] == "PARTIALLY_PAID"
    with pytest.raises(ValueError, match="vượt quá"):
        database.add_membership_bill_payment(bill["id"], payment(600_001))
    assert next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )["display_status"] == "PENDING_PAYMENT"

    database.add_membership_bill_payment(bill["id"], payment(600_000))
    membership = next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )
    assert membership["display_status"] == "ACTIVE"
    assert membership["card_status"] == "ACTIVE"
    card_token = database.connection.execute(
        "SELECT card_token FROM membership_cards WHERE membership_id = ?",
        (membership_id,),
    ).fetchone()["card_token"]
    verified = database.verify_membership_card(card_token)
    assert verified["status"] == "ACTIVE"
    assert verified["plan_name"] == "Gold"


def test_renewal_preserves_remaining_term_and_extends_card(database):
    customer_id = create_customer(database)
    membership_id = database.create_membership(customer_id, create_plan(database))
    first_bill = database.list_membership_bills()[0]
    database.add_membership_bill_payment(first_bill["id"], payment(1_000_000))
    before = next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )
    original_end = date.fromisoformat(before["end_date"])

    renewal_bill_id = database.create_membership_renewal(membership_id)
    renewal_bill = next(
        item for item in database.list_membership_bills()
        if item["id"] == renewal_bill_id
    )
    with pytest.raises(ValueError, match="chưa thanh toán"):
        database.create_membership_renewal(membership_id)
    database.add_membership_bill_payment(
        renewal_bill_id, payment(renewal_bill["total_amount"])
    )
    after = next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )

    assert date.fromisoformat(after["end_date"]) == original_end + timedelta(days=30)
    assert after["renewal_count"] == 1
    assert after["card_expiry"] == after["end_date"]


def test_free_plan_is_activated_without_fake_payment(database):
    customer_id = create_customer(database)
    membership_id = database.create_membership(customer_id, create_plan(database, 0))
    membership = next(
        item for item in database.list_memberships() if item["id"] == membership_id
    )
    bill = database.list_membership_bills()[0]

    assert membership["display_status"] == "ACTIVE"
    assert membership["card_status"] == "ACTIVE"
    assert bill["status"] == "PAID"
    assert bill["amount_paid"] == 0
    assert database.list_membership_bill_payments(bill["id"]) == []
