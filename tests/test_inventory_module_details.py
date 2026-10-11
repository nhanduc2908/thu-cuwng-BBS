from datetime import date, timedelta

import pytest

from app.database import Database
from app.modules.inventory.demand import forecast_demand
from app.modules.inventory.expiry import expiry_bucket
from app.modules.inventory.replenishment import recommend_replenishment
from app.modules.inventory.validation import validate_day_count, validate_date_range


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "inventory_details.db")
    yield instance
    instance.close()


def create_item(database, minimum_stock=2):
    return database.save_inventory_item(
        {
            "item_code": "DETAIL-FOOD",
            "name": "Thức ăn chi tiết",
            "category": "FOOD",
            "unit": "kg",
            "minimum_stock": minimum_stock,
        }
    )


def test_demand_forecast_and_replenishment_use_usable_stock(database):
    item_id = create_item(database)
    batch_id = database.receive_inventory_stock(
        item_id,
        {
            "batch_code": "DETAIL-BATCH",
            "quantity": 10,
            "unit_cost": 100,
            "occurred_on": date.today().isoformat(),
        },
    )
    animal_id = database.save_animal(
        {
            "animal_code": "DETAIL-PET",
            "name": "Milo",
            "species": "Chó",
            "status": "AVAILABLE",
        }
    )
    database.consume_inventory_stock(
        item_id,
        {
            "quantity": 6,
            "animal_id": animal_id,
            "occurred_on": date.today().isoformat(),
        },
    )

    forecast = database.forecast_inventory_demand(item_id, 30, 30)
    assert forecast["consumed_quantity"] == 6
    assert forecast["average_daily_quantity"] == 0.2
    assert forecast["days_of_stock"] == 20

    suggestions = database.inventory_replenishment_suggestions(
        lead_time_days=7, safety_days=7, window_days=30
    )
    suggestion = next(item for item in suggestions if item["item_id"] == item_id)
    assert suggestion["item_id"] == item_id
    assert suggestion["suggested_quantity"] == pytest.approx(0.8)
    assert database.list_inventory_batches(item_id)[0]["id"] == batch_id


def test_stock_valuation_and_ledger_reconciliation(database):
    item_id = create_item(database)
    database.receive_inventory_stock(
        item_id,
        {
            "batch_code": "VALUE-BATCH",
            "quantity": 5,
            "unit_cost": 120,
            "occurred_on": date.today().isoformat(),
        },
    )
    valuation = next(
        item
        for item in database.inventory_stock_valuation()
        if item["item_id"] == item_id
    )
    assert valuation["stock_value"] == 600
    assert valuation["stock_quantity"] == 5

    batch = database.list_inventory_batches(item_id)[0]
    with database.connection:
        database.connection.execute(
            "UPDATE inventory_batches SET quantity_remaining = 4 WHERE id = ?",
            (batch["id"],),
        )
    discrepancies = database.inventory_ledger_discrepancies(item_id)
    assert discrepancies == [
        {
            "batch_id": batch["id"],
            "item_id": item_id,
            "batch_code": "VALUE-BATCH",
            "recorded_quantity": 4.0,
            "ledger_quantity": 5.0,
            "difference": -1.0,
        }
    ]


def test_expiry_category_trace_and_animal_consumption_reports(database):
    item_id = create_item(database)
    database.receive_inventory_stock(
        item_id,
        {
            "batch_code": "TRACE-BATCH",
            "quantity": 5,
            "unit_cost": 40,
            "expiry_date": (date.today() + timedelta(days=5)).isoformat(),
            "occurred_on": date.today().isoformat(),
        },
    )
    animal_id = database.save_animal(
        {
            "animal_code": "TRACE-PET",
            "name": "Luna",
            "species": "Mèo",
            "status": "AVAILABLE",
        }
    )
    database.consume_inventory_stock(
        item_id,
        {
            "quantity": 2,
            "animal_id": animal_id,
            "occurred_on": date.today().isoformat(),
        },
    )

    overview = database.inventory_expiry_overview()
    assert overview["summary"]["DUE_7_DAYS"]["batch_count"] == 1
    assert database.inventory_category_overview()[0]["category"] == "FOOD"
    trace = database.trace_inventory_batch("TRACE-BATCH")
    assert [line["balance_after"] for line in trace["timeline"]] == [5, 3]
    assert trace["ledger_quantity"] == 3
    consumption = database.inventory_animal_consumption(
        date.today().isoformat(), date.today().isoformat()
    )
    assert consumption[0]["animal_id"] == animal_id
    assert consumption[0]["quantity"] == 2
    assert consumption[0]["cost"] == 80


def test_inventory_calculation_helpers_validate_and_handle_boundaries():
    forecast = forecast_demand(1, 15, 3, 15, 10)
    assert forecast.average_daily_quantity == 1
    assert forecast.days_of_stock == 3
    suggestion = recommend_replenishment(
        item_id=1,
        item_code="FOOD-1",
        name="Food",
        average_daily_quantity=1,
        usable_quantity=3,
        minimum_stock=2,
        lead_time_days=2,
        safety_days=1,
        days_of_stock=3,
    )
    assert suggestion.target_quantity == 5
    assert suggestion.suggested_quantity == 2
    assert expiry_bucket(None) == "NO_EXPIRY"
    assert expiry_bucket((date.today() - timedelta(days=1)).isoformat()) == "EXPIRED"
    assert validate_day_count("7", "days") == 7
    assert validate_date_range("2026-01-01", "2026-01-02")[0] == date(2026, 1, 1)
    with pytest.raises(ValueError):
        validate_day_count(0, "days")
    with pytest.raises(ValueError):
        validate_date_range("2026-02-01", "2026-01-01")
