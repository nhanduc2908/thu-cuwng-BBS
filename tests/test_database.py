import sqlite3

import pytest

from app.database import (
    ANIMAL_PROFILE_FIELDS,
    CARE_CHECKLIST_ITEMS,
    Database,
)


@pytest.fixture
def database(tmp_path):
    instance = Database(tmp_path / "test.db")
    yield instance
    instance.close()


def animal_values(code="PET-001"):
    return {
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
        "sale_price": 2_000_000,
        "status": "AVAILABLE",
        "health_status": "Bình thường",
        "description": "",
    }


def test_create_search_and_update_animal(database):
    animal_id = database.save_animal(animal_values())

    assert database.get_animal(animal_id)["name"] == "Milo"
    assert len(database.list_animals("PET-001")) == 1
    assert database.dashboard_counts()["AVAILABLE"] == 1

    updated = animal_values()
    updated["name"] = "Milo mới"
    database.save_animal(updated, animal_id)
    assert database.get_animal(animal_id)["name"] == "Milo mới"


def test_duplicate_code_is_rejected(database):
    database.save_animal(animal_values())

    with pytest.raises(sqlite3.IntegrityError):
        database.save_animal(animal_values())


def test_health_record_updates_animal_health_status(database):
    animal_id = database.save_animal(animal_values())
    database.add_health_record(
        {
            "animal_id": animal_id,
            "examination_date": "2026-09-27",
            "health_status": "Theo dõi",
            "diagnosis": "Cảm nhẹ",
            "treatment": "Theo dõi",
            "veterinarian": "BS An",
            "note": "",
        }
    )

    assert database.get_animal(animal_id)["health_status"] == "Theo dõi"
    assert len(database.list_health_records()) == 1


def test_care_tasks_and_animal_history_prevent_accidental_delete(database):
    animal_id = database.save_animal(animal_values())
    task_id = database.add_care_task(
        {
            "animal_id": animal_id,
            "title": "Cho ăn",
            "scheduled_at": "2026-09-27T08:00",
            "assigned_to": "Lan",
            "note": "",
        }
    )
    database.set_care_task_completed(task_id, True)

    assert database.list_care_tasks()[0]["is_completed"] == 1
    with pytest.raises(sqlite3.IntegrityError):
        database.delete_animal(animal_id)


def test_animal_profile_has_25_persisted_characteristics(database):
    values = animal_values()
    values.update(
        {
            "supplier_name": "Nhà cung cấp A",
            "intake_date": "2026-09-20",
            "microchip_id": "CHIP-001",
            "cage_location": "Khu A-1",
            "diet": "Thức ăn hạt",
            "feeding_schedule": "08:00 và 18:00",
            "allergies": "Không rõ",
            "vaccination_status": "Đã tiêm mũi 1",
            "last_vet_visit": "2026-09-25",
            "exercise_needs": "Vận động 30 phút mỗi ngày",
            "behavior": "Thân thiện",
        }
    )

    animal_id = database.save_animal(values)
    saved = database.get_animal(animal_id)

    assert len(ANIMAL_PROFILE_FIELDS) == 25
    assert {field for field in ANIMAL_PROFILE_FIELDS if field not in saved.keys()} == set()
    assert saved["diet"] == "Thức ăn hạt"
    assert saved["microchip_id"] == "CHIP-001"


def test_checklist_saves_all_25_items_and_updates_same_assessment(database):
    animal_id = database.save_animal(animal_values())
    checklist = [
        {"item_key": key, "status": "OK", "note": ""}
        for key, _ in CARE_CHECKLIST_ITEMS
    ]

    database.save_care_checklist(
        animal_id, "2026-09-27", "Lan", checklist
    )
    checklist[0] = {
        "item_key": CARE_CHECKLIST_ITEMS[0][0],
        "status": "NEEDS_ATTENTION",
        "note": "Ăn ít hơn thường ngày",
    }
    database.save_care_checklist(
        animal_id, "2026-09-27", "Lan", checklist
    )
    saved = database.get_care_checklist(animal_id, "2026-09-27")

    assert len(CARE_CHECKLIST_ITEMS) == 25
    assert len(saved) == 25
    assert saved[CARE_CHECKLIST_ITEMS[0][0]]["status"] == "NEEDS_ATTENTION"
    assert saved[CARE_CHECKLIST_ITEMS[0][0]]["note"] == "Ăn ít hơn thường ngày"


def test_vaccination_due_alerts_are_reported(database):
    animal_id = database.save_animal(animal_values("PET-998"))
    database.add_vaccination_record(
        {
            "animal_id": animal_id,
            "vaccine_name": "Dại",
            "administered_at": "2026-09-01",
            "next_due_at": "2026-10-02",
            "dose_number": 1,
            "veterinarian": "BS Nhi",
            "note": "Cần nhắc lại",
            "status": "SCHEDULED",
        }
    )

    alerts = database.list_operational_alerts()
    assert any(
        alert["category"] == "Tiêm phòng" and "Dại" in alert["title"]
        for alert in alerts
    )


def test_existing_animal_database_is_migrated(tmp_path):
    legacy_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(legacy_path)
    connection.execute(
        """
        CREATE TABLE animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT NOT NULL DEFAULT '',
            gender TEXT NOT NULL DEFAULT 'Chưa rõ',
            birth_date TEXT NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '',
            weight REAL,
            origin TEXT NOT NULL DEFAULT '',
            purchase_price REAL NOT NULL DEFAULT 0,
            sale_price REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'PENDING_INSPECTION',
            health_status TEXT NOT NULL DEFAULT 'Bình thường',
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()

    migrated = Database(legacy_path)
    try:
        columns = {
            row["name"]
            for row in migrated.connection.execute("PRAGMA table_info(animals)")
        }
        assert "diet" in columns
        assert "microchip_id" in columns
        assert "behavior" in columns
        assert "must_change_password" in {
            row["name"]
            for row in migrated.connection.execute("PRAGMA table_info(users)")
        }
        membership_columns = {
            row["name"]
            for row in migrated.connection.execute(
                "PRAGMA table_info(membership_plans)"
            )
        }
        assert {
            "billing_mode",
            "included_visits",
            "service_category",
        } <= membership_columns
        assert migrated.connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'service_appointments'
            """
        ).fetchone()
        assert "cycle_number" in {
            row["name"]
            for row in migrated.connection.execute(
                "PRAGMA table_info(membership_service_uses)"
            )
        }
        inventory_columns = {
            row["name"]
            for row in migrated.connection.execute(
                "PRAGMA table_info(inventory_items)"
            )
        }
        assert {
            "animal_subspecies",
            "age_min_months",
            "age_max_months",
            "life_stage",
            "food_type",
            "suitable_weight_min",
            "vitamin_c_content",
            "water_level",
            "diet_type",
        } <= inventory_columns
        assert migrated.connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'feeding_age_rules'
            """
        ).fetchone()
        assert migrated.connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'animal_intake_receipts'
            """
        ).fetchone()
        assert migrated.connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'care_checklists'"
        ).fetchone()
    finally:
        migrated.close()


def cage_values(code="CAGE-01", **overrides):
    values = {
        "cage_code": code,
        "name": "Chuồng A1",
        "area": "Khu A",
        "accepted_species": "",
        "capacity": 2,
        "description": "",
    }
    values.update(overrides)
    return values


def test_cage_assignment_enforces_capacity_and_tracks_location(database):
    cage_id = database.save_cage(cage_values(capacity=1))
    animal_id = database.save_animal(animal_values())

    database.assign_animal_to_cage(animal_id, cage_id, "Nhập chuồng")

    cage = database.get_cage(cage_id)
    assert cage["current_count"] == 1
    assert cage["assigned_count"] == 1
    assert database.get_animal(animal_id)["cage_location"] == "Chuồng A1"
    assert database.list_cage_animals(cage_id)[0]["id"] == animal_id

    second_animal_id = database.save_animal(animal_values("PET-002"))
    with pytest.raises(ValueError, match="đầy"):
        database.assign_animal_to_cage(second_animal_id, cage_id)


def test_moving_animal_updates_counts_and_preserves_assignment_history(database):
    first_cage_id = database.save_cage(cage_values("CAGE-01", capacity=1))
    second_cage_id = database.save_cage(
        cage_values("CAGE-02", name="Chuồng B1", capacity=2)
    )
    animal_id = database.save_animal(animal_values())
    database.assign_animal_to_cage(animal_id, first_cage_id)
    database.assign_animal_to_cage(animal_id, second_cage_id, "Chuyển khu")
    database.assign_animal_to_cage(animal_id, second_cage_id, "Không đổi chuồng")

    assert database.get_cage(first_cage_id)["current_count"] == 0
    assert database.get_cage(second_cage_id)["current_count"] == 1
    assert database.get_animal(animal_id)["cage_location"] == "Chuồng B1"
    history = database.connection.execute(
        """
        SELECT cage_id, released_at FROM animal_cage_assignments
        WHERE animal_id = ? ORDER BY id
        """,
        (animal_id,),
    ).fetchall()
    assert len(history) == 2
    assert history[0]["released_at"] is not None
    assert history[1]["cage_id"] == second_cage_id
    assert history[1]["released_at"] is None


def test_cage_species_capacity_and_history_rules(database):
    cat_cage_id = database.save_cage(
        cage_values(accepted_species="Mèo", capacity=2)
    )
    dog_cage_id = database.save_cage(
        cage_values("CAGE-02", name="Chuồng chó", accepted_species="Chó")
    )
    animal_id = database.save_animal(animal_values())

    with pytest.raises(ValueError, match="chỉ nhận loài Chó"):
        database.assign_animal_to_cage(animal_id, dog_cage_id)

    database.assign_animal_to_cage(animal_id, cat_cage_id)
    second_animal_id = database.save_animal(animal_values("PET-002"))
    database.assign_animal_to_cage(second_animal_id, cat_cage_id)
    with pytest.raises(ValueError, match="không thể thấp hơn"):
        database.save_cage(cage_values(capacity=1), cat_cage_id)
    with pytest.raises(ValueError, match="đang có động vật thuộc loài"):
        database.save_cage(
            cage_values(accepted_species="Chó", capacity=2), cat_cage_id
        )
    changed_species = animal_values()
    changed_species["species"] = "Chó"
    with pytest.raises(ValueError, match="Không thể đổi loài"):
        database.save_animal(changed_species, animal_id)
    with pytest.raises(ValueError, match="đang có động vật"):
        database.delete_cage(cat_cage_id)

    database.unassign_animal_from_cage(animal_id)
    database.unassign_animal_from_cage(second_animal_id)
    assert database.get_animal(animal_id)["cage_location"] == ""
    assert database.get_cage(cat_cage_id)["current_count"] == 0
    database.set_cage_active(cat_cage_id, False)
    with pytest.raises(ValueError, match="ngừng hoạt động"):
        database.assign_animal_to_cage(animal_id, cat_cage_id)
    database.set_cage_active(cat_cage_id, True)
    with pytest.raises(ValueError, match="lịch sử"):
        database.delete_cage(cat_cage_id)

    history = database.list_cage_history(cat_cage_id)
    assert len(history) == 2
    assert all(record["released_at"] for record in history)


def supplier_values(code="SUP-001", **overrides):
    values = {
        "supplier_code": code,
        "name": "Nhà cung cấp thú cưng",
        "contact_person": "Nguyễn An",
        "phone": "0900000000",
        "email": "supplier@example.test",
        "address": "Hà Nội",
        "tax_code": "",
        "note": "",
    }
    values.update(overrides)
    return values


def import_batch_values(supplier_id, code="IMP-2026-001"):
    return {
        "batch_code": code,
        "supplier_id": supplier_id,
        "import_date": "2026-09-27",
        "note": "",
    }


def intake_evidence():
    return {
        "photo_data": b"\xff\xd8\xffpet intake photo",
        "photo_mime": "image/jpeg",
        "received_by": "Nhân viên tiếp nhận",
        "confirmation": "Đã nhận bé tại cửa hàng",
    }


def test_supplier_batch_intake_and_passing_inspection(database):
    supplier_id = database.save_supplier(supplier_values())
    batch_id = database.create_import_batch(import_batch_values(supplier_id))
    animal_id = database.add_import_animal(
        batch_id,
        {
            "animal_code": "PET-IMP-001",
            "name": "Milo",
            "species": "Mèo",
            "breed": "Mèo ta",
            "purchase_price": 1_000_000,
            "sale_price": 2_000_000,
            **intake_evidence(),
        },
    )

    animal = database.get_animal(animal_id)
    assert animal["status"] == "PENDING_INSPECTION"
    assert animal["supplier_name"] == "Nhà cung cấp thú cưng"
    assert animal["received_at"]
    assert animal["received_by"] == "Nhân viên tiếp nhận"
    receipt = database.get_intake_receipt(animal_id)
    assert receipt["photo_data"] == b"\xff\xd8\xffpet intake photo"
    assert receipt["confirmation"] == "Đã nhận bé tại cửa hàng"
    assert database.list_import_batches()[0]["animal_count"] == 1
    assert database.list_import_animals(batch_id)[0]["receipt_confirmed"]
    assert database.list_import_animals(batch_id)[0]["inspection_result"] is None

    database.record_inspection(
        batch_id,
        {
            "animal_id": animal_id,
            "inspected_at": "2026-09-27",
            "result": "PASSED",
            "symptoms": "",
            "checked_by": "BS An",
            "note": "Đạt kiểm tra đầu vào",
        },
    )

    assert database.get_animal(animal_id)["status"] == "AVAILABLE"
    assert database.list_import_batches()[0]["status"] == "COMPLETED"
    assert database.list_import_batches()[0]["inspected_count"] == 1
    assert len(database.list_inspections(batch_id, animal_id)) == 1


@pytest.mark.parametrize(
    ("result", "expected_status", "expected_health"),
    (
        ("QUARANTINE", "QUARANTINE", "Theo dõi"),
        ("NEEDS_TREATMENT", "TREATMENT", "Đang điều trị"),
    ),
)
def test_import_inspection_routes_animal_to_care_status(
    database, result, expected_status, expected_health
):
    supplier_id = database.save_supplier(supplier_values())
    batch_id = database.create_import_batch(import_batch_values(supplier_id))
    animal_id = database.add_import_animal(
        batch_id,
        {
            "animal_code": "PET-IMP-002",
            "name": "Miu",
            "species": "Mèo",
            **intake_evidence(),
        },
    )

    database.record_inspection(
        batch_id,
        {
            "animal_id": animal_id,
            "inspected_at": "2026-09-27",
            "result": result,
            "symptoms": "Cần theo dõi",
            "checked_by": "BS An",
            "note": "",
        },
    )

    animal = database.get_animal(animal_id)
    assert animal["status"] == expected_status
    assert animal["health_status"] == expected_health
    assert database.list_import_batches()[0]["status"] == "COMPLETED"


def test_imports_reject_inactive_supplier_and_cancel_empty_batches(database):
    supplier_id = database.save_supplier(supplier_values())
    database.set_supplier_active(supplier_id, False)
    with pytest.raises(ValueError, match="ngừng hoạt động"):
        database.create_import_batch(import_batch_values(supplier_id))

    database.set_supplier_active(supplier_id, True)
    batch_id = database.create_import_batch(import_batch_values(supplier_id))
    with pytest.raises(ValueError, match="Không tìm thấy lô nhập"):
        database.cancel_import_batch(batch_id + 1)
    database.cancel_import_batch(batch_id)
    with pytest.raises(ValueError, match="đang tiếp nhận"):
        database.add_import_animal(
            batch_id,
            {"animal_code": "PET-IMP-003", "name": "Miu", "species": "Mèo"},
        )

    populated_batch_id = database.create_import_batch(
        import_batch_values(supplier_id, "IMP-2026-002")
    )
    database.add_import_animal(
        populated_batch_id,
        {
            "animal_code": "PET-IMP-004",
            "name": "Milo",
            "species": "Mèo",
            **intake_evidence(),
        },
    )
    with pytest.raises(ValueError, match="đã có động vật"):
        database.cancel_import_batch(populated_batch_id)


def test_intake_requires_photo_confirmation_and_staff_member(database):
    supplier_id = database.save_supplier(supplier_values())
    batch_id = database.create_import_batch(import_batch_values(supplier_id))
    with pytest.raises(ValueError, match="ảnh xác nhận"):
        database.add_import_animal(
            batch_id,
            {"animal_code": "PET-NO-PHOTO", "name": "Miu", "species": "Mèo"},
        )
    assert database.list_import_animals(batch_id) == []

    with pytest.raises(ValueError, match="xác nhận bé"):
        database.add_import_animal(
            batch_id,
            {
                "animal_code": "PET-NO-CONFIRM",
                "name": "Miu",
                "species": "Mèo",
                **{**intake_evidence(), "confirmation": ""},
            },
        )
    assert database.list_import_animals(batch_id) == []

    with pytest.raises(ValueError, match="không khớp"):
        database.add_import_animal(
            batch_id,
            {
                "animal_code": "PET-BAD-PHOTO",
                "name": "Miu",
                "species": "Mèo",
                **{**intake_evidence(), "photo_data": b"not an image"},
            },
        )
    assert database.list_import_animals(batch_id) == []


def test_first_admin_password_authentication_permissions_and_audit(database):
    admin_id = database.create_initial_admin(
        "Admin", "Quản trị cửa hàng", "StrongPass!2026"
    )
    assert database.user_count() == 1
    assert database.authenticate("admin", "StrongPass!2026")["id"] == admin_id
    assert database.authenticate("admin", "incorrect-password") is None
    assert database.has_permission(admin_id, "users.manage")

    with pytest.raises(ValueError, match="đã được thiết lập"):
        database.create_initial_admin("second-admin", "Admin 2", "OtherPass!2026")
    with pytest.raises(ValueError, match="ít nhất 10"):
        database.create_user(
            "short", "Short Password", "short", "CAREGIVER", admin_id
        )

    caregiver_id = database.create_user(
        "care", "Nhân viên chăm sóc", "CarePass!2026", "CAREGIVER", admin_id
    )
    assert not database.has_permission(caregiver_id, "users.manage")
    assert database.has_permission(caregiver_id, "care.manage")
    assert database.authenticate("care", "CarePass!2026")["id"] == caregiver_id

    database.change_password(
        caregiver_id, "CarePass!2026", "NewCarePass!2026", caregiver_id
    )
    assert database.authenticate("care", "CarePass!2026") is None
    assert database.authenticate("care", "NewCarePass!2026")["id"] == caregiver_id

    events = database.list_audit_events()
    assert any(event["action"] == "INITIAL_ADMIN" for event in events)
    assert any(
        event["action"] == "CHANGE_PASSWORD" and event["actor_id"] == caregiver_id
        for event in events
    )
    with pytest.raises(sqlite3.IntegrityError, match="audit log is immutable"):
        database.connection.execute(
            "UPDATE audit_logs SET details = 'tampered' WHERE id = ?",
            (events[0]["id"],),
        )


def test_default_admin_and_local_recovery_require_password_change(database):
    default_admin_id = database.create_default_admin()
    user = database.authenticate("ADMIN", "admin")
    assert user["id"] == default_admin_id
    assert user["must_change_password"] is True
    with pytest.raises(ValueError, match="đã được thiết lập"):
        database.create_default_admin()

    database.change_password(
        default_admin_id,
        "admin",
        "StrongPass!2026",
        default_admin_id,
    )
    user = database.authenticate("admin", "StrongPass!2026")
    assert user["must_change_password"] is False

    database.create_user(
        "backup-admin", "Quản trị dự phòng", "OtherPass!2026", "ADMIN"
    )
    database.auth.set_user_active(default_admin_id, False)
    database.reset_admin_login()
    recovered_user = database.authenticate("admin", "admin")
    assert recovered_user["id"] == default_admin_id
    assert recovered_user["must_change_password"] is True
    assert database.has_permission(default_admin_id, "users.manage")
    assert any(
        event["action"] == "ADMIN_PASSWORD_RESET"
        for event in database.audit.list_events()
    )


def test_last_active_admin_cannot_be_demoted_or_disabled(database):
    admin_id = database.create_initial_admin(
        "admin", "Quản trị", "StrongPass!2026"
    )

    with pytest.raises(ValueError, match="quản trị viên.*cuối cùng"):
        database.set_user_role(admin_id, "MANAGER")
    with pytest.raises(ValueError, match="quản trị viên.*cuối cùng"):
        database.set_user_active(admin_id, False, admin_id)


def test_logged_in_user_cannot_write_outside_role_permissions(database):
    admin_id = database.create_initial_admin(
        "admin", "Quản trị", "StrongPass!2026"
    )
    animal_id = database.save_animal(animal_values())
    caregiver_id = database.create_user(
        "care", "Nhân viên chăm sóc", "CarePass!2026", "CAREGIVER", admin_id
    )
    database.set_actor(caregiver_id)

    with pytest.raises(PermissionError, match="animals.manage"):
        database.save_animal(animal_values())

    task_id = database.add_care_task(
        {
            "animal_id": animal_id,
            "title": "Cho ăn",
            "scheduled_at": "2026-09-28T08:00",
            "assigned_to": "Nhân viên",
            "note": "",
        }
    )
    assert task_id > 0
    with pytest.raises(PermissionError, match="audit.view"):
        database.list_audit_events()
    event = database.audit.list_events(entity_type="care_task")[0]
    assert event["actor_id"] == caregiver_id
