from datetime import date, timedelta

import pytest

from app.database import Database
from app.modules.inventory.catalog_seed import COMBO_DEFINITIONS, PRODUCT_GROUPS


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "catalog.db")
    yield instance
    instance.close()


def create_customer(database, code="CUS-PRODUCT"):
    return database.save_customer(
        {"customer_code": code, "name": "Khách mua hàng", "phone": "0900000000"}
    )


def receive(database, item_id, quantity, batch_code="LOT-1"):
    database.receive_inventory_stock(
        item_id,
        {
            "batch_code": batch_code,
            "quantity": quantity,
            "unit_cost": 1000,
            "expiry_date": None,
            "occurred_on": date.today().isoformat(),
            "reference": "PO-DEMO",
            "note": "",
        },
    )


def make_product_order(database, customer_id, item_id, quantity, code):
    return database.create_product_sales_order(
        {
            "order_code": code,
            "customer_id": customer_id,
            "ordered_at": date.today().isoformat(),
            "product_lines": [{"item_id": item_id, "quantity": quantity}],
            "combo_lines": [],
        }
    )


def test_catalog_seed_is_idempotent_and_combo_skus_are_linked(database):
    first_products = database.list_inventory_items()
    first_combos = database.list_inventory_combos()
    assert 600 <= len(first_products) <= 650
    assert len({row["item_code"] for row in first_products}) == len(first_products)
    assert len(first_combos) == len(COMBO_DEFINITIONS) == 8
    assert {row["catalog_category"] for row in first_products if row["is_demo"]} >= {
        group["name"] for group in PRODUCT_GROUPS
    }
    assert all(combo["component_count"] > 0 for combo in first_combos)
    group_sizes = {}
    for product in first_products:
        if product["is_demo"]:
            category = product["catalog_category"]
            group_sizes[category] = group_sizes.get(category, 0) + 1
    assert len(group_sizes) == 20
    assert all(20 <= count <= 40 for count in group_sizes.values())
    assert {
        row["catalog_category"] for row in first_products if row["is_demo"]
    } >= {
        "Chim cảnh",
        "Chuột cảnh",
        "Bò sát cảnh",
    }
    assert not any("vaccine" in row["name"].casefold() for row in first_products)

    database.inventory.seed_catalog()

    assert len(database.list_inventory_items()) == len(first_products)
    assert len(database.list_inventory_combos()) == len(first_combos)


def test_feeding_metadata_seed_is_idempotent_and_does_not_create_stock(database):
    first_items = database.list_inventory_items()
    first_profiles = {
        item["id"]: (
            item["animal_subspecies"],
            item["age_min_months"],
            item["age_max_months"],
            item["life_stage"],
            item["food_category"],
            item["food_type"],
        )
        for item in first_items
        if item["is_demo"] and item["food_type"]
    }
    first_rules = database.inventory.list_age_rules(active_only=False)
    batch_count = database.connection.execute(
        "SELECT COUNT(*) FROM inventory_batches"
    ).fetchone()[0]

    assert first_profiles
    assert len(first_profiles) >= 100
    assert first_rules
    database.inventory.seed_feeding_profiles()

    second_profiles = {
        item["id"]: (
            item["animal_subspecies"],
            item["age_min_months"],
            item["age_max_months"],
            item["life_stage"],
            item["food_category"],
            item["food_type"],
        )
        for item in database.list_inventory_items()
        if item["is_demo"] and item["food_type"]
    }
    assert second_profiles == first_profiles
    assert len(database.inventory.list_age_rules(active_only=False)) == len(first_rules)
    assert database.connection.execute(
        "SELECT COUNT(*) FROM inventory_batches"
    ).fetchone()[0] == batch_count


def test_feeding_recommendations_use_seeded_stage_and_usable_stock(database):
    puppy = next(
        item
        for item in database.list_inventory_items()
        if item["item_code"] == "DEMO-DOG-FOOD-001"
    )
    adult = next(
        item
        for item in database.list_inventory_items()
        if item["item_code"] == "DEMO-DOG-FOOD-002"
    )
    assert puppy["food_type"]
    assert puppy["life_stage"] == "YOUNG"
    assert adult["life_stage"] == "ADULT"
    receive(database, puppy["id"], 2, "PUPPY-LOT")
    receive(database, adult["id"], 2, "ADULT-LOT")
    animal_id = database.save_animal(
        {
            "animal_code": "PET-FEED-001",
            "name": "Milo",
            "species": "Chó",
            "breed": "Corgi",
            "birth_date": (date.today() - timedelta(days=120)).isoformat(),
            "weight": 8,
        }
    )
    result = database.inventory.recommend_feeding_products(
        database.get_animal(animal_id)
    )

    assert [item["item_code"] for item in result["products"]] == [
        "DEMO-DOG-FOOD-001"
    ]


def test_food_metadata_can_be_saved_and_updated(database):
    item_id = database.save_inventory_item(
        {
            "item_code": "TEST-FEED-001",
            "name": "Thức ăn thử cho chó",
            "category": "FOOD",
            "unit": "gói",
            "target_species": "Chó",
            "animal_subspecies": "Chó nhà",
            "age_min_months": 2,
            "age_max_months": 24,
            "age_unit": "MONTH",
            "life_stage": "YOUNG",
            "food_category": "COMPLETE",
            "food_type": "DRY",
            "protein_source": "Cá",
            "serving_size": "Theo nhãn",
            "vitamin_c_content": "Không bổ sung",
        }
    )
    item = database.get_inventory_item(item_id)
    assert item["age_min_months"] == 2
    assert item["food_type"] == "DRY"
    assert item["protein_source"] == "Cá"

    database.save_inventory_item(
        {
            "item_code": "TEST-FEED-001",
            "name": "Thức ăn thử cho chó",
            "category": "FOOD",
            "unit": "gói",
            "target_species": "Chó",
            "age_min_months": 3,
            "age_max_months": 36,
            "age_unit": "YEAR",
            "life_stage": "ADULT",
            "food_type": "WET",
        },
        item_id,
    )
    updated = database.get_inventory_item(item_id)
    assert updated["age_min_months"] == 3
    assert updated["age_unit"] == "YEAR"
    assert updated["food_type"] == "WET"


def test_product_sale_uses_membership_price_reserves_stock_and_deducts_when_paid(database):
    customer_id = create_customer(database)
    plan_id = database.save_membership_plan(
        {
            "code": "MEMBER10",
            "name": "Member 10%",
            "duration_days": 365,
            "price": 0,
            "discount_percent": 10,
        }
    )
    membership_id = database.create_membership(customer_id, plan_id)
    item = next(
        item
        for item in database.list_inventory_items()
        if item["item_code"] == "DEMO-DOG-FOOD-001"
    )
    receive(database, item["id"], 5)

    catalog_item = next(
        product
        for product in database.list_saleable_products(customer_id)
        if product["id"] == item["id"]
    )
    assert catalog_item["sale_price"] == 76_500

    order_id = make_product_order(database, customer_id, item["id"], 2, "SO-P-001")
    order = next(row for row in database.list_sales_orders() if row["id"] == order_id)
    assert order["total_amount"] == 153_000
    assert order["item_count"] == 1
    assert database.get_inventory_item(item["id"])["usable_quantity"] == 5
    assert next(
        product
        for product in database.list_saleable_products(customer_id)
        if product["id"] == item["id"]
    )["available"] == 3

    with pytest.raises(ValueError, match="không đủ"):
        make_product_order(database, customer_id, item["id"], 4, "SO-P-002")

    database.add_payment(
        order_id,
        {
            "amount": 50_000,
            "method": "CASH",
            "paid_at": date.today().isoformat(),
            "reference": "",
        },
    )
    assert database.get_inventory_item(item["id"])["usable_quantity"] == 5
    database.add_payment(
        order_id,
        {
            "amount": 103_000,
            "method": "CASH",
            "paid_at": date.today().isoformat(),
            "reference": "",
        },
    )
    assert database.get_inventory_item(item["id"])["usable_quantity"] == 3
    assert database.list_inventory_movements(item["id"])[0]["movement_type"] == "OUT"
    assert next(
        item
        for item in database.list_memberships()
        if item["id"] == membership_id
    )["display_status"] == "ACTIVE"


def test_combo_sale_deducts_each_component_and_uses_combo_price(database):
    customer_id = create_customer(database)
    combo = next(
        item
        for item in database.list_inventory_combos(active_only=True)
        if item["combo_code"] == "COMBO-PUPPY"
    )
    components = database.list_inventory_combo_items(combo["id"])
    for index, component in enumerate(components, start=1):
        receive(database, component["item_id"], 3, f"COMBO-LOT-{index}")

    available_combo = next(
        item
        for item in database.list_saleable_combos(customer_id)
        if item["id"] == combo["id"]
    )
    assert available_combo["available"] is True
    order_id = database.create_product_sales_order(
        {
            "order_code": "SO-COMBO-001",
            "customer_id": customer_id,
            "ordered_at": date.today().isoformat(),
            "product_lines": [],
            "combo_lines": [{"combo_id": combo["id"], "quantity": 1}],
        }
    )
    order = next(row for row in database.list_sales_orders() if row["id"] == order_id)
    assert order["total_amount"] == combo["sale_price"]
    assert order["item_count"] == 1
    database.add_payment(
        order_id,
        {
            "amount": combo["sale_price"],
            "method": "CASH",
            "paid_at": date.today().isoformat(),
            "reference": "",
        },
    )
    for component in components:
        item = database.get_inventory_item(component["item_id"])
        assert item["usable_quantity"] == 3 - component["quantity"]
