from datetime import date, datetime, timedelta

import pytest

from app.database import Database
from app.modules.services.repository import SERVICE_CATEGORIES


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "services.db")
    yield instance
    instance.close()


def create_customer(database, code="CUS-SERVICE"):
    return database.save_customer(
        {"customer_code": code, "name": "Khách dịch vụ", "phone": "0900000000"}
    )


def create_package(database, **overrides):
    values = {
        "code": "TEST-BATH",
        "category": "BATH",
        "name": "Tắm kiểm thử",
        "description": "Gói kiểm thử",
        "species": "Chó, Mèo",
        "coat_types": "LONG,DOUBLE,CURLY,THICK",
        "min_weight": 0,
        "max_weight": None,
        "duration_minutes": 60,
        "list_price": 100_000,
        "member_price": None,
        "included_weight_kg": 5,
        "surcharge_per_kg": 10_000,
        "coat_surcharge": 20_000,
    }
    values.update(overrides)
    return database.save_service_package(values)


def create_membership(database, customer_id, **overrides):
    values = {
        "code": "TEST-MEMBER",
        "name": "Gói dịch vụ kiểm thử",
        "duration_days": 30,
        "price": 0,
        "discount_percent": 0,
        "billing_mode": "PREPAID_VISITS",
        "included_visits": 1,
        "service_category": "BATH",
    }
    values.update(overrides)
    plan_id = database.save_membership_plan(values)
    return database.create_membership(customer_id, plan_id)


def appointment_values(customer_id, package_id, **overrides):
    values = {
        "customer_id": customer_id,
        "package_id": package_id,
        "pet_name": "Milo",
        "species": "Chó",
        "weight_kg": 8,
        "coat_type": "Dài",
        "scheduled_at": (datetime.now() + timedelta(days=1)).isoformat(timespec="minutes"),
        "assigned_staff": "Nhân viên A",
        "note": "",
    }
    values.update(overrides)
    return values


def advance_to_in_progress(database, appointment_id):
    database.update_service_appointment_status(appointment_id, "CHECKED_IN")
    database.update_service_appointment_status(appointment_id, "IN_PROGRESS")


def test_service_catalog_seeds_exact_categories_idempotently(database):
    assert len(database.list_service_packages()) == 240
    packages_by_category = {
        category: sum(
            package["category"] == category
            for package in database.list_service_packages()
        )
        for category in SERVICE_CATEGORIES
    }
    assert set(packages_by_category.values()) == {40}
    assert sum(
        plan["code"].startswith("SVC-MEM-")
        for plan in database.list_membership_plans()
    ) == 40
    assert {
        plan["billing_mode"]
        for plan in database.list_membership_plans()
        if plan["code"].startswith("SVC-MEM-")
    } == {"PREPAID_VISITS", "MEMBER_DISCOUNT", "RECURRING"}

    before = len(database.list_service_packages())
    assert database.services.seed_catalog() == (240, 40)
    assert len(database.list_service_packages()) == before


def test_quote_adds_configured_weight_and_coat_surcharges_and_member_discount(database):
    customer_id = create_customer(database)
    package_id = create_package(database)
    quote = database.get_service_quote(
        package_id, "Chó", 8, "Dài"
    )
    assert quote == {
        "base_price": 100_000,
        "surcharge": 50_000,
        "discount": 0,
        "total_price": 150_000,
        "billing_mode": None,
    }

    member_id = create_membership(
        database,
        customer_id,
        code="TEST-DISCOUNT",
        billing_mode="MEMBER_DISCOUNT",
        included_visits=0,
        discount_percent=10,
    )
    discounted = database.get_service_quote(
        package_id, "Chó", 8, "Dài", member_id
    )
    assert discounted["discount"] == 10_000
    assert discounted["total_price"] == 140_000
    with pytest.raises(ValueError, match="loài"):
        database.get_service_quote(package_id, "Thỏ", 8, "Dài")


def test_completed_service_creates_bill_and_valid_payment_can_settle_it(database):
    customer_id = create_customer(database)
    package_id = create_package(database, coat_surcharge=0)
    appointment_id = database.create_service_appointment(
        appointment_values(customer_id, package_id)
    )
    advance_to_in_progress(database, appointment_id)
    database.update_service_appointment_status(appointment_id, "COMPLETED")

    appointment = next(
        row
        for row in database.list_service_appointments()
        if row["id"] == appointment_id
    )
    assert appointment["status"] == "COMPLETED"
    assert appointment["bill_status"] == "PENDING"
    bill = next(
        row
        for row in database.list_membership_bills()
        if row["id"] == appointment["bill_id"]
    )
    assert bill["bill_type"] == "OTHER"
    assert bill["total_amount"] == 130_000
    database.add_membership_bill_payment(
        bill["id"],
        {
            "amount": 130_000,
            "method": "CASH",
            "paid_at": date.today().isoformat(),
        },
    )
    bill = next(
        row
        for row in database.list_membership_bills()
        if row["id"] == appointment["bill_id"]
    )
    assert bill["status"] == "PAID"


def test_booking_rejects_overlapping_pet_or_staff_appointments(database):
    customer_id = create_customer(database)
    package_id = create_package(database, coat_surcharge=0)
    values = appointment_values(customer_id, package_id)
    first = database.create_service_appointment(values)
    with pytest.raises(ValueError, match="trùng giờ"):
        database.create_service_appointment(values)
    database.update_service_appointment_status(first, "CANCELLED")
    assert database.create_service_appointment(values)


def test_rescheduling_keeps_prepaid_credit_reserved_and_validates_conflicts(database):
    customer_id = create_customer(database)
    package_id = create_package(database)
    membership_id = create_membership(database, customer_id)
    appointment_id = database.create_service_appointment(
        appointment_values(
            customer_id,
            package_id,
            membership_id=membership_id,
            weight_kg=8,
            coat_type="Dài",
        )
    )
    new_schedule = (datetime.now() + timedelta(days=3)).isoformat(
        timespec="minutes"
    )

    database.reschedule_service_appointment(appointment_id, new_schedule)

    appointment = next(
        row
        for row in database.list_service_appointments()
        if row["id"] == appointment_id
    )
    assert appointment["scheduled_at"] == new_schedule
    assert database.list_customer_service_memberships(customer_id)[0]["remaining_visits"] == 0
    database.update_service_appointment_status(appointment_id, "CANCELLED")
    assert database.list_customer_service_memberships(customer_id)[0]["remaining_visits"] == 1


def test_caregiver_can_manage_bookings_but_not_service_catalog(database):
    customer_id = create_customer(database)
    package_id = create_package(database, coat_surcharge=0)
    admin_id = database.create_initial_admin(
        "admin", "Quản trị", "Admin-pass-2026!"
    )
    caregiver_id = database.create_user(
        "care", "Nhân viên chăm sóc", "Care-pass-2026!", "CAREGIVER", admin_id
    )
    database.set_actor(caregiver_id)

    appointment_id = database.create_service_appointment(
        appointment_values(customer_id, package_id)
    )
    assert appointment_id > 0
    with pytest.raises(PermissionError):
        database.save_service_package(
            {
                "code": "CARE-EDIT",
                "category": "BATH",
                "name": "Không được sửa catalog",
                "species": "Chó, Mèo",
                "duration_minutes": 60,
                "list_price": 0,
            }
        )


def test_prepaid_visits_are_reserved_released_on_cancel_and_used_on_completion(database):
    customer_id = create_customer(database)
    package_id = create_package(database)
    membership_id = create_membership(database, customer_id)
    values = appointment_values(
        customer_id,
        package_id,
        membership_id=membership_id,
        weight_kg=8,
        coat_type="Dài",
    )
    first = database.create_service_appointment(values)
    assert next(
        row
        for row in database.list_service_appointments()
        if row["id"] == first
    )["total_price"] == 50_000
    overbooked = {
        **values,
        "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat(
            timespec="minutes"
        ),
    }
    with pytest.raises(ValueError, match="hết lượt"):
        database.create_service_appointment(overbooked)

    database.update_service_appointment_status(first, "CANCELLED")
    second = database.create_service_appointment(values)
    advance_to_in_progress(database, second)
    database.update_service_appointment_status(second, "COMPLETED")
    remaining = database.list_customer_service_memberships(customer_id)[0]
    assert remaining["remaining_visits"] == 0
    completed = next(
        row
        for row in database.list_service_appointments()
        if row["id"] == second
    )
    bill = next(
        row
        for row in database.list_membership_bills()
        if row["id"] == completed["bill_id"]
    )
    assert bill["total_amount"] == 50_000


def test_successful_membership_renewal_restores_prepaid_visit_allowance(database):
    customer_id = create_customer(database)
    package_id = create_package(
        database, included_weight_kg=8, coat_surcharge=0
    )
    membership_id = create_membership(
        database, customer_id, price=100_000
    )
    initial_bill = database.list_membership_bills()[0]
    database.add_membership_bill_payment(
        initial_bill["id"],
        {
            "amount": 100_000,
            "method": "CASH",
            "paid_at": date.today().isoformat(),
        },
    )
    appointment_id = database.create_service_appointment(
        appointment_values(
            customer_id,
            package_id,
            membership_id=membership_id,
            weight_kg=8,
            coat_type="Ngắn",
        )
    )
    advance_to_in_progress(database, appointment_id)
    database.update_service_appointment_status(appointment_id, "COMPLETED")
    assert database.list_customer_service_memberships(customer_id)[0]["remaining_visits"] == 0

    renewal_bill_id = database.create_membership_renewal(membership_id)
    renewal_bill = next(
        row for row in database.list_membership_bills()
        if row["id"] == renewal_bill_id
    )
    database.add_membership_bill_payment(
        renewal_bill_id,
        {
            "amount": renewal_bill["total_amount"],
            "method": "CASH",
            "paid_at": date.today().isoformat(),
        },
    )
    assert database.list_customer_service_memberships(customer_id)[0]["remaining_visits"] == 1
