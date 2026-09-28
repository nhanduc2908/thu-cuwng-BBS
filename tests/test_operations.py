import sqlite3
from datetime import date

import pytest

from app.database import Database


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "operations.db")
    yield instance
    instance.close()


def test_reports_filter_date_ranges_and_include_current_inventory(database):
    item_id = database.save_inventory_item(
        {
            "item_code": "MED-1",
            "name": "Thuốc bổ",
            "category": "MEDICINE",
            "unit": "lọ",
            "minimum_stock": 0,
        }
    )
    database.receive_inventory_stock(
        item_id,
        {
            "batch_code": "LOT-1",
            "quantity": 4,
            "expiry_date": None,
            "unit_cost": 10,
            "occurred_on": "2026-09-20",
        },
    )
    animal_id = database.save_animal(
        {
            "animal_code": "PET-1",
            "name": "Milo",
            "species": "Mèo",
            "sale_price": 100,
            "status": "AVAILABLE",
        }
    )
    database.add_health_record(
        {
            "animal_id": animal_id,
            "examination_date": "2026-09-20",
            "health_status": "Bình thường",
            "diagnosis": "",
            "treatment": "",
            "veterinarian": "BS An",
            "note": "",
        }
    )

    assert database.report_inventory()[0]["usable_quantity"] == 4
    assert len(database.report_health("2026-09-01", "2026-09-30")) == 1
    assert database.report_health("2026-09-21", "2026-09-30") == []
    with pytest.raises(ValueError, match="Khoảng thời gian"):
        database.report_sales("2026-09-30", "2026-09-01")


def test_operational_alerts_include_due_care_and_low_stock(database):
    item_id = database.save_inventory_item(
        {
            "item_code": "FOOD-1",
            "name": "Thức ăn",
            "category": "FOOD",
            "unit": "kg",
            "minimum_stock": 2,
        }
    )
    animal_id = database.save_animal(
        {
            "animal_code": "PET-1",
            "name": "Milo",
            "species": "Mèo",
            "sale_price": 100,
            "status": "AVAILABLE",
        }
    )
    database.add_care_task(
        {
            "animal_id": animal_id,
            "title": "Cho ăn sáng",
            "scheduled_at": f"{date.today().isoformat()}T07:00",
            "assigned_to": "Lan",
            "note": "",
        }
    )

    alerts = database.list_operational_alerts()
    assert {alert["category"] for alert in alerts} >= {"Tồn kho", "Chăm sóc"}


def test_backup_creates_consistent_database_and_refuses_overwrite(database, tmp_path):
    database.save_setting("backup_directory", str(tmp_path))
    destination = tmp_path / "backup.db"

    assert database.backup_to(destination) == destination.resolve()
    backup = sqlite3.connect(destination)
    try:
        assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert backup.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = 'backup_directory'"
        ).fetchone()[0] == str(tmp_path)
    finally:
        backup.close()
    with pytest.raises(FileExistsError, match="đã tồn tại"):
        database.backup_to(destination)
    with pytest.raises(ValueError, match="không thể trùng"):
        database.backup_to(database.path)


def test_inventory_writes_and_backup_are_permission_gated(database, tmp_path):
    admin_id = database.create_initial_admin("admin", "Admin", "Admin-pass-123")
    database.set_actor(admin_id)
    staff_id = database.create_user(
        "sales", "Sales", "Sales-pass-123", "SALES"
    )
    database.set_actor(staff_id)

    with pytest.raises(PermissionError, match="inventory.manage"):
        database.save_inventory_item(
            {
                "item_code": "MED-1",
                "name": "Thuốc",
                "category": "MEDICINE",
                "unit": "lọ",
            }
        )
    with pytest.raises(PermissionError, match="settings.manage"):
        database.backup_to(tmp_path / "denied.db")
