from pathlib import Path
import sqlite3
from typing import Any

from app.modules.animals.constants import (
    ANIMAL_PROFILE_FIELDS,
    ANIMAL_STATUSES,
)
from app.modules.animals.repository import AnimalRepository
from app.modules.audit.repository import AuditRepository
from app.modules.auth.repository import AuthRepository
from app.modules.care.constants import (
    CARE_CHECKLIST_ITEMS,
    CARE_CHECKLIST_STATUSES,
)
from app.modules.care.repository import CareRepository
from app.modules.customers.repository import CustomerRepository
from app.modules.dashboard.repository import DashboardRepository
from app.modules.health.repository import HealthRepository
from app.modules.imports.repository import ImportRepository
from app.modules.suppliers.repository import SupplierRepository
from app.modules.store.repository import StoreRepository
from app.modules.sales.repository import SalesRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.reports.repository import ReportRepository
from app.modules.notifications.repository import NotificationRepository


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self.auth = AuthRepository(self.connection)
        self.audit = AuditRepository(self.connection)
        self.animals = AnimalRepository(self.connection)
        self.health = HealthRepository(self.connection)
        self.care = CareRepository(self.connection)
        self.dashboard = DashboardRepository(self.connection)
        self.store = StoreRepository(self.connection)
        self.suppliers = SupplierRepository(self.connection)
        self.imports = ImportRepository(self.connection)
        self.customers = CustomerRepository(self.connection)
        self.sales = SalesRepository(self.connection)
        self.inventory = InventoryRepository(self.connection)
        self.reports = ReportRepository(self.connection)
        self.notifications = NotificationRepository(self.connection)
        self.actor_id: int | None = None

    def _create_tables(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS animals (
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
                    purchase_price REAL NOT NULL DEFAULT 0 CHECK (purchase_price >= 0),
                    sale_price REAL NOT NULL DEFAULT 0 CHECK (sale_price >= 0),
                    status TEXT NOT NULL DEFAULT 'PENDING_INSPECTION'
                        CHECK (status IN (
                            'PENDING_INSPECTION', 'AVAILABLE', 'RESERVED', 'SOLD',
                            'QUARANTINE', 'TREATMENT', 'TRANSFERRED', 'DECEASED'
                        )),
                    health_status TEXT NOT NULL DEFAULT 'Bình thường',
                    description TEXT NOT NULL DEFAULT '',
                    supplier_name TEXT NOT NULL DEFAULT '',
                    intake_date TEXT NOT NULL DEFAULT '',
                    microchip_id TEXT NOT NULL DEFAULT '',
                    cage_location TEXT NOT NULL DEFAULT '',
                    diet TEXT NOT NULL DEFAULT '',
                    feeding_schedule TEXT NOT NULL DEFAULT '',
                    allergies TEXT NOT NULL DEFAULT '',
                    vaccination_status TEXT NOT NULL DEFAULT '',
                    last_vet_visit TEXT NOT NULL DEFAULT '',
                    exercise_needs TEXT NOT NULL DEFAULT '',
                    behavior TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS health_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    examination_date TEXT NOT NULL,
                    health_status TEXT NOT NULL,
                    diagnosis TEXT NOT NULL DEFAULT '',
                    treatment TEXT NOT NULL DEFAULT '',
                    veterinarian TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS care_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    title TEXT NOT NULL,
                    scheduled_at TEXT NOT NULL,
                    assigned_to TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1))
                );

                CREATE TABLE IF NOT EXISTS care_checklists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    checklist_date TEXT NOT NULL,
                    item_key TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('OK', 'NEEDS_ATTENTION', 'NOT_APPLICABLE')
                    ),
                    note TEXT NOT NULL DEFAULT '',
                    checked_by TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (animal_id, checklist_date, item_key)
                );

                CREATE TABLE IF NOT EXISTS cages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cage_code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    area TEXT NOT NULL DEFAULT '',
                    accepted_species TEXT NOT NULL DEFAULT '',
                    capacity INTEGER NOT NULL CHECK (capacity > 0),
                    current_count INTEGER NOT NULL DEFAULT 0
                        CHECK (current_count >= 0 AND current_count <= capacity),
                    description TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS animal_cage_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    cage_id INTEGER NOT NULL REFERENCES cages(id) ON DELETE RESTRICT,
                    assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    released_at TEXT,
                    note TEXT NOT NULL DEFAULT ''
                );

                CREATE UNIQUE INDEX IF NOT EXISTS
                    idx_animal_cage_assignments_one_active
                ON animal_cage_assignments(animal_id)
                WHERE released_at IS NULL;

                CREATE INDEX IF NOT EXISTS idx_cage_assignments_cage_active
                ON animal_cage_assignments(cage_id, released_at);

                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    contact_person TEXT NOT NULL DEFAULT '',
                    phone TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    tax_code TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS import_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_code TEXT NOT NULL UNIQUE,
                    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
                    import_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'OPEN'
                        CHECK (status IN ('OPEN', 'COMPLETED', 'CANCELLED')),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS import_batch_animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER NOT NULL REFERENCES import_batches(id) ON DELETE RESTRICT,
                    animal_id INTEGER NOT NULL UNIQUE REFERENCES animals(id) ON DELETE RESTRICT,
                    cost REAL NOT NULL DEFAULT 0 CHECK (cost >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER NOT NULL REFERENCES import_batches(id) ON DELETE RESTRICT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    inspected_at TEXT NOT NULL,
                    result TEXT NOT NULL
                        CHECK (result IN ('PASSED', 'QUARANTINE', 'NEEDS_TREATMENT')),
                    symptoms TEXT NOT NULL DEFAULT '',
                    checked_by TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (
                        role IN ('ADMIN', 'MANAGER', 'VETERINARIAN', 'CAREGIVER', 'SALES')
                    ),
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    password_changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER,
                    details TEXT NOT NULL DEFAULT '',
                    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    order_id INTEGER REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    reserved_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    deposit REAL NOT NULL DEFAULT 0 CHECK (deposit >= 0),
                    status TEXT NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE', 'CONVERTED', 'RELEASED', 'EXPIRED')),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    closed_at TEXT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_reservations_animal_active
                    ON reservations(animal_id) WHERE status = 'ACTIVE';

                CREATE TABLE IF NOT EXISTS sales_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_code TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    ordered_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'OPEN'
                        CHECK (status IN ('OPEN', 'PARTIALLY_PAID', 'PAID', 'CANCELLED')),
                    total_amount REAL NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    paid_at TEXT
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    animal_id INTEGER NOT NULL UNIQUE REFERENCES animals(id) ON DELETE RESTRICT,
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    amount REAL NOT NULL CHECK (amount > 0),
                    method TEXT NOT NULL CHECK (
                        method IN ('CASH', 'BANK_TRANSFER', 'CARD', 'OTHER')
                    ),
                    paid_at TEXT NOT NULL,
                    reference TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reservation_deposits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reservation_id INTEGER NOT NULL REFERENCES reservations(id) ON DELETE RESTRICT,
                    amount REAL NOT NULL CHECK (amount > 0),
                    paid_at TEXT NOT NULL,
                    method TEXT NOT NULL CHECK (
                        method IN ('CASH', 'BANK_TRANSFER', 'CARD', 'OTHER')
                    ),
                    reference TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reservation_refunds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reservation_id INTEGER NOT NULL REFERENCES reservations(id) ON DELETE RESTRICT,
                    amount REAL NOT NULL CHECK (amount > 0),
                    refunded_at TEXT NOT NULL,
                    method TEXT NOT NULL CHECK (
                        method IN ('CASH', 'BANK_TRANSFER', 'CARD', 'OTHER')
                    ),
                    reference TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL CHECK (category IN ('FOOD', 'MEDICINE')),
                    unit TEXT NOT NULL,
                    minimum_stock REAL NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
                    description TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS inventory_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    batch_code TEXT NOT NULL,
                    expiry_date TEXT,
                    quantity_remaining REAL NOT NULL CHECK (quantity_remaining >= 0),
                    unit_cost REAL NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (item_id, batch_code)
                );

                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    batch_id INTEGER NOT NULL REFERENCES inventory_batches(id) ON DELETE RESTRICT,
                    movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    occurred_on TEXT NOT NULL,
                    animal_id INTEGER REFERENCES animals(id) ON DELETE RESTRICT,
                    reference TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_audit_logs_occurred
                    ON audit_logs(occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_logs_actor
                    ON audit_logs(actor_id, occurred_at DESC);

                CREATE INDEX IF NOT EXISTS idx_import_batches_supplier_date
                    ON import_batches(supplier_id, import_date);
                CREATE INDEX IF NOT EXISTS idx_import_animals_batch
                    ON import_batch_animals(batch_id, animal_id);
                CREATE INDEX IF NOT EXISTS idx_inspections_batch_animal
                    ON inspections(batch_id, animal_id, inspected_at);
                CREATE INDEX IF NOT EXISTS idx_inventory_batches_item_expiry
                    ON inventory_batches(item_id, expiry_date, quantity_remaining);
                CREATE INDEX IF NOT EXISTS idx_inventory_movements_item_date
                    ON inventory_movements(item_id, occurred_on DESC);
                """
            )
            animal_columns = {
                row["name"]
                for row in self.connection.execute("PRAGMA table_info(animals)")
            }
            added_columns = {
                "supplier_name": "TEXT NOT NULL DEFAULT ''",
                "intake_date": "TEXT NOT NULL DEFAULT ''",
                "microchip_id": "TEXT NOT NULL DEFAULT ''",
                "cage_location": "TEXT NOT NULL DEFAULT ''",
                "diet": "TEXT NOT NULL DEFAULT ''",
                "feeding_schedule": "TEXT NOT NULL DEFAULT ''",
                "allergies": "TEXT NOT NULL DEFAULT ''",
                "vaccination_status": "TEXT NOT NULL DEFAULT ''",
                "last_vet_visit": "TEXT NOT NULL DEFAULT ''",
                "exercise_needs": "TEXT NOT NULL DEFAULT ''",
                "behavior": "TEXT NOT NULL DEFAULT ''",
            }
            for column, definition in added_columns.items():
                if column not in animal_columns:
                    self.connection.execute(
                        f"ALTER TABLE animals ADD COLUMN {column} {definition}"
                    )

            self.connection.executescript(
                """
                CREATE TRIGGER IF NOT EXISTS audit_logs_no_update
                BEFORE UPDATE ON audit_logs
                BEGIN
                    SELECT RAISE(ABORT, 'audit log is immutable');
                END;

                CREATE TRIGGER IF NOT EXISTS audit_logs_no_delete
                BEFORE DELETE ON audit_logs
                BEGIN
                    SELECT RAISE(ABORT, 'audit log is immutable');
                END;
                """
            )

    def dashboard_counts(self) -> dict[str, int]:
        return self.dashboard.dashboard_counts()

    def recent_animals(self, limit: int = 5) -> list[sqlite3.Row]:
        return self.dashboard.recent_animals(limit)

    def list_animals(
        self, search: str = "", status: str | None = None
    ) -> list[sqlite3.Row]:
        return self.animals.list_animals(search, status)

    def get_animal(self, animal_id: int) -> sqlite3.Row | None:
        return self.animals.get_animal(animal_id)

    def save_animal(self, values: dict[str, Any], animal_id: int | None = None) -> int:
        self._require_permission("animals.manage")
        result = self.animals.save_animal(values, animal_id)
        self._audit("UPDATE" if animal_id is not None else "CREATE", "animal", result)
        return result

    def delete_animal(self, animal_id: int) -> None:
        self._require_permission("animals.manage")
        self.animals.delete_animal(animal_id)
        self._audit("DELETE", "animal", animal_id)

    def list_health_records(self) -> list[sqlite3.Row]:
        return self.health.list_health_records()

    def add_health_record(self, values: dict[str, Any]) -> int:
        self._require_permission("health.manage")
        result = self.health.add_health_record(values)
        self._audit("CREATE", "health_record", result)
        return result

    def list_care_tasks(self) -> list[sqlite3.Row]:
        return self.care.list_care_tasks()

    def add_care_task(self, values: dict[str, Any]) -> int:
        self._require_permission("care.manage")
        result = self.care.add_care_task(values)
        self._audit("CREATE", "care_task", result)
        return result

    def set_care_task_completed(self, task_id: int, completed: bool) -> None:
        self._require_permission("care.manage")
        self.care.set_care_task_completed(task_id, completed)
        self._audit("COMPLETE" if completed else "REOPEN", "care_task", task_id)

    def get_care_checklist(
        self, animal_id: int, checklist_date: str
    ) -> dict[str, sqlite3.Row]:
        return self.care.get_care_checklist(animal_id, checklist_date)

    def save_care_checklist(
        self,
        animal_id: int,
        checklist_date: str,
        checked_by: str,
        items: list[dict[str, str]],
    ) -> None:
        self._require_permission("care.manage")
        self.care.save_care_checklist(
            animal_id, checklist_date, checked_by, items
        )
        self._audit(
            "SAVE_CHECKLIST",
            "animal",
            animal_id,
            f"date={checklist_date}; items={len(items)}",
        )

    def list_cages(self, search: str = "") -> list[sqlite3.Row]:
        return self.store.list_cages(search)

    def get_cage(self, cage_id: int) -> sqlite3.Row | None:
        return self.store.get_cage(cage_id)

    def save_cage(self, values: dict[str, Any], cage_id: int | None = None) -> int:
        self._require_permission("store.manage")
        result = self.store.save_cage(values, cage_id)
        self._audit("UPDATE" if cage_id is not None else "CREATE", "cage", result)
        return result

    def delete_cage(self, cage_id: int) -> None:
        self._require_permission("store.manage")
        self.store.delete_cage(cage_id)
        self._audit("DELETE", "cage", cage_id)

    def set_cage_active(self, cage_id: int, active: bool) -> None:
        self._require_permission("store.manage")
        self.store.set_cage_active(cage_id, active)
        self._audit("ACTIVATE" if active else "DEACTIVATE", "cage", cage_id)

    def list_cage_animals(self, cage_id: int) -> list[sqlite3.Row]:
        return self.store.list_cage_animals(cage_id)

    def list_cage_history(self, cage_id: int) -> list[sqlite3.Row]:
        return self.store.list_cage_history(cage_id)

    def assign_animal_to_cage(self, animal_id: int, cage_id: int, note: str = "") -> None:
        self._require_permission("store.manage")
        self.store.assign_animal_to_cage(animal_id, cage_id, note)
        self._audit("ASSIGN", "animal_cage", animal_id, f"cage_id={cage_id}")

    def unassign_animal_from_cage(self, animal_id: int) -> None:
        self._require_permission("store.manage")
        self.store.unassign_animal_from_cage(animal_id)
        self._audit("UNASSIGN", "animal_cage", animal_id)

    def list_suppliers(self, search: str = "") -> list[sqlite3.Row]:
        return self.suppliers.list_suppliers(search)

    def get_supplier(self, supplier_id: int) -> sqlite3.Row | None:
        return self.suppliers.get_supplier(supplier_id)

    def save_supplier(
        self, values: dict[str, Any], supplier_id: int | None = None
    ) -> int:
        self._require_permission("imports.manage")
        result = self.suppliers.save_supplier(values, supplier_id)
        self._audit(
            "UPDATE" if supplier_id is not None else "CREATE", "supplier", result
        )
        return result

    def set_supplier_active(self, supplier_id: int, active: bool) -> None:
        self._require_permission("imports.manage")
        self.suppliers.set_supplier_active(supplier_id, active)
        self._audit(
            "ACTIVATE" if active else "DEACTIVATE", "supplier", supplier_id
        )

    def list_import_batches(self, search: str = "") -> list[sqlite3.Row]:
        return self.imports.list_batches(search)

    def create_import_batch(self, values: dict[str, Any]) -> int:
        self._require_permission("imports.manage")
        result = self.imports.create_batch(values)
        self._audit("CREATE", "import_batch", result)
        return result

    def list_import_animals(self, batch_id: int) -> list[sqlite3.Row]:
        return self.imports.list_batch_animals(batch_id)

    def add_import_animal(self, batch_id: int, values: dict[str, Any]) -> int:
        self._require_permission("imports.manage")
        result = self.imports.add_animal_to_batch(batch_id, values)
        self._audit(
            "INTAKE", "animal", result, f"batch_id={batch_id}"
        )
        return result

    def record_inspection(self, batch_id: int, values: dict[str, Any]) -> int:
        self._require_permission("imports.manage")
        result = self.imports.record_inspection(batch_id, values)
        self._audit(
            "INSPECT",
            "animal",
            values["animal_id"],
            f"batch_id={batch_id}; result={values['result']}",
        )
        return result

    def list_inspections(
        self, batch_id: int, animal_id: int | None = None
    ) -> list[sqlite3.Row]:
        return self.imports.list_inspections(batch_id, animal_id)

    def cancel_import_batch(self, batch_id: int) -> None:
        self._require_permission("imports.manage")
        self.imports.cancel_empty_batch(batch_id)
        self._audit("CANCEL", "import_batch", batch_id)

    def list_customers(self, search: str = "") -> list[sqlite3.Row]:
        return self.customers.list_customers(search)

    def get_customer(self, customer_id: int) -> sqlite3.Row | None:
        return self.customers.get_customer(customer_id)

    def save_customer(
        self, values: dict[str, Any], customer_id: int | None = None
    ) -> int:
        self._require_permission("sales.manage")
        result = self.customers.save_customer(values, customer_id)
        self._audit(
            "UPDATE" if customer_id is not None else "CREATE", "customer", result
        )
        return result

    def list_reservations(self) -> list[sqlite3.Row]:
        return self.sales.list_reservations()

    def list_saleable_animals(self) -> list[sqlite3.Row]:
        return self.sales.list_saleable_animals()

    def get_order_balance(self, order_id: int) -> float:
        return self.sales.get_order_balance(order_id)

    def get_reservation_balance(self, reservation_id: int) -> float:
        return self.sales.get_reservation_balance(reservation_id)

    def create_reservation(self, values: dict[str, Any]) -> int:
        self._require_permission("sales.manage")
        result = self.sales.create_reservation(values)
        self._audit(
            "RESERVE",
            "animal",
            values["animal_id"],
            f"reservation_id={result}; customer_id={values['customer_id']}",
        )
        return result

    def release_reservation(self, reservation_id: int, expired: bool = False) -> None:
        self._require_permission("sales.manage")
        self.sales.release_reservation(
            reservation_id, "EXPIRED" if expired else "RELEASED"
        )
        self._audit(
            "EXPIRE_RESERVATION" if expired else "RELEASE_RESERVATION",
            "reservation",
            reservation_id,
        )

    def list_sales_orders(self) -> list[sqlite3.Row]:
        return self.sales.list_orders()

    def list_order_items(self, order_id: int) -> list[sqlite3.Row]:
        return self.sales.list_order_items(order_id)

    def create_sales_order(self, values: dict[str, Any]) -> int:
        self._require_permission("sales.manage")
        result = self.sales.create_order(values)
        self._audit(
            "CREATE_ORDER",
            "sales_order",
            result,
            f"customer_id={values['customer_id']}; animals={values['animal_ids']}",
        )
        return result

    def add_payment(self, order_id: int, values: dict[str, Any]) -> int:
        self._require_permission("sales.manage")
        result = self.sales.add_payment(order_id, values)
        self._audit(
            "PAYMENT",
            "sales_order",
            order_id,
            f"amount={values['amount']}; method={values['method']}",
        )
        return result

    def cancel_sales_order(self, order_id: int) -> None:
        self._require_permission("sales.manage")
        self.sales.cancel_unpaid_order(order_id)
        self._audit("CANCEL_ORDER", "sales_order", order_id)

    def list_order_payments(self, order_id: int) -> list[sqlite3.Row]:
        return self.sales.list_payments(order_id)

    def list_reservation_deposits(
        self, reservation_id: int
    ) -> list[sqlite3.Row]:
        return self.sales.list_reservation_deposits(reservation_id)

    def refund_reservation_deposit(
        self, reservation_id: int, values: dict[str, Any]
    ) -> int:
        self._require_permission("sales.manage")
        result = self.sales.refund_reservation_deposit(reservation_id, values)
        self._audit(
            "REFUND_DEPOSIT",
            "reservation",
            reservation_id,
            f"amount={values['amount']}; method={values['method']}",
        )
        return result

    def list_reservation_refunds(
        self, reservation_id: int
    ) -> list[sqlite3.Row]:
        return self.sales.list_reservation_refunds(reservation_id)

    def list_inventory_items(self, search: str = "") -> list[sqlite3.Row]:
        return self.inventory.list_items(search)

    def get_inventory_item(self, item_id: int) -> sqlite3.Row | None:
        return self.inventory.get_item(item_id)

    def save_inventory_item(
        self, values: dict[str, Any], item_id: int | None = None
    ) -> int:
        self._require_permission("inventory.manage")
        result = self.inventory.save_item(values, item_id)
        self._audit(
            "UPDATE" if item_id is not None else "CREATE",
            "inventory_item",
            result,
        )
        return result

    def receive_inventory_stock(
        self, item_id: int, values: dict[str, Any]
    ) -> int:
        self._require_permission("inventory.manage")
        batch_id = self.inventory.receive_stock(item_id, values)
        self._audit(
            "STOCK_IN",
            "inventory_batch",
            batch_id,
            f"item_id={item_id}; quantity={values['quantity']}",
        )
        return batch_id

    def consume_inventory_stock(
        self, item_id: int, values: dict[str, Any]
    ) -> list[int]:
        self._require_permission("inventory.manage")
        movement_ids = self.inventory.consume_stock(item_id, values)
        self._audit(
            "STOCK_OUT",
            "inventory_item",
            item_id,
            f"quantity={values['quantity']}; animal_id={values.get('animal_id')}",
        )
        return movement_ids

    def list_inventory_batches(self, item_id: int) -> list[sqlite3.Row]:
        return self.inventory.list_batches(item_id)

    def list_inventory_movements(self, item_id: int) -> list[sqlite3.Row]:
        return self.inventory.list_movements(item_id)

    def low_stock_items(self) -> list[sqlite3.Row]:
        return self.inventory.low_stock_items()

    def expiring_inventory_batches(self, days: int = 30) -> list[sqlite3.Row]:
        return self.inventory.expiring_batches(days)

    def set_inventory_item_active(self, item_id: int, active: bool) -> None:
        self._require_permission("inventory.manage")
        self.inventory.set_item_active(item_id, active)
        self._audit(
            "ACTIVATE" if active else "DEACTIVATE", "inventory_item", item_id
        )

    def report_inventory(self) -> list[sqlite3.Row]:
        self._require_permission("reports.view")
        return self.reports.inventory()

    def report_sales(
        self, start_date: str, end_date: str
    ) -> list[sqlite3.Row]:
        self._require_permission("reports.view")
        return self.reports.sales(start_date, end_date)

    def report_health(
        self, start_date: str, end_date: str
    ) -> list[sqlite3.Row]:
        self._require_permission("reports.view")
        return self.reports.health(start_date, end_date)

    def list_operational_alerts(self) -> list[dict[str, Any]]:
        self._require_permission("notifications.view")
        return self.notifications.list_alerts()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.connection.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        return row["setting_value"] if row else default

    def save_setting(self, key: str, value: str) -> None:
        self._require_permission("settings.manage")
        if not key.strip():
            raise ValueError("Khóa thiết lập không được để trống.")
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO app_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key.strip(), value),
            )
        self._audit("UPDATE_SETTING", "app_setting", None, key.strip())

    def backup_to(self, destination: str | Path) -> Path:
        self._require_permission("settings.manage")
        target = Path(destination).expanduser().resolve()
        if target == self.path.expanduser().resolve():
            raise ValueError("Tệp sao lưu không thể trùng với cơ sở dữ liệu đang dùng.")
        if target.exists():
            raise FileExistsError(f"Tệp sao lưu đã tồn tại: {target}")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Thư mục sao lưu không tồn tại: {target.parent}")
        temporary = target.with_name(f".{target.name}.tmp")
        if temporary.exists():
            raise FileExistsError(f"Tệp tạm sao lưu đã tồn tại: {temporary}")
        backup_connection = sqlite3.connect(temporary)
        try:
            self.connection.backup(backup_connection)
            backup_connection.close()
            temporary.rename(target)
        except BaseException:
            backup_connection.close()
            if temporary.exists():
                temporary.unlink()
            raise
        self._audit("BACKUP", "database", None, target.name)
        return target

    def user_count(self) -> int:
        return self.auth.user_count()

    def list_users(self) -> list[sqlite3.Row]:
        self._require_permission("users.manage")
        return self.auth.list_users()

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        return self.auth.authenticate(username, password)

    def create_initial_admin(
        self, username: str, display_name: str, password: str
    ) -> int:
        user_id = self.auth.create_initial_admin(username, display_name, password)
        self.audit.record(
            user_id, "INITIAL_ADMIN", "user", user_id, "Initial administrator setup"
        )
        return user_id

    def create_user(
        self,
        username: str,
        display_name: str,
        password: str,
        role: str,
        actor_id: int | None = None,
    ) -> int:
        self._require_permission("users.manage")
        user_id = self.auth.create_user(username, display_name, password, role)
        self.audit.record(
            actor_id if actor_id is not None else self.actor_id,
            "CREATE",
            "user",
            user_id,
            f"username={username.strip().casefold()}; role={role}",
        )
        return user_id

    def set_user_role(
        self, user_id: int, role: str, actor_id: int | None = None
    ) -> None:
        self._require_permission("users.manage")
        acting_user_id = actor_id if actor_id is not None else self.actor_id
        if acting_user_id == user_id:
            raise ValueError("Không thể tự thay đổi vai trò của tài khoản đang đăng nhập.")
        self.auth.set_user_role(user_id, role)
        self.audit.record(
            acting_user_id,
            "UPDATE_ROLE",
            "user",
            user_id,
            f"role={role}",
        )

    def set_user_active(
        self, user_id: int, active: bool, actor_id: int | None = None
    ) -> None:
        self._require_permission("users.manage")
        acting_user_id = actor_id if actor_id is not None else self.actor_id
        if acting_user_id == user_id and not active:
            current = self.auth.list_users()
            selected = next((user for user in current if user["id"] == user_id), None)
            if selected and selected["role"] == "ADMIN":
                active_admins = sum(
                    1
                    for user in current
                    if user["role"] == "ADMIN" and user["is_active"]
                )
                if active_admins > 1:
                    raise ValueError(
                        "Không thể tự khóa tài khoản quản trị đang đăng nhập."
                    )
        self.auth.set_user_active(user_id, active)
        self.audit.record(
            acting_user_id,
            "ACTIVATE" if active else "DEACTIVATE",
            "user",
            user_id,
        )

    def change_password(
        self, user_id: int, current: str, new: str, actor_id: int | None = None
    ) -> None:
        self.auth.change_password(user_id, current, new)
        self.audit.record(
            actor_id if actor_id is not None else self.actor_id,
            "CHANGE_PASSWORD",
            "user",
            user_id,
        )

    def has_permission(self, user_id: int, permission: str) -> bool:
        return self.auth.has_permission(user_id, permission)

    def record_audit(
        self,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        details: str = "",
    ) -> int:
        return self.audit.record(actor_id, action, entity_type, entity_id, details)

    def list_audit_events(
        self,
        limit: int = 500,
        actor_id: int | None = None,
        entity_type: str | None = None,
    ) -> list[sqlite3.Row]:
        self._require_permission("audit.view")
        return self.audit.list_events(limit, actor_id, entity_type)

    def close(self) -> None:
        self.connection.close()

    def set_actor(self, user_id: int | None) -> None:
        if user_id is not None:
            if not self.auth.has_permission(user_id, "dashboard.view"):
                raise PermissionError("Tài khoản không có quyền truy cập ứng dụng.")
        self.actor_id = user_id

    def _require_permission(self, permission: str) -> None:
        if self.actor_id is not None and not self.auth.has_permission(
            self.actor_id, permission
        ):
            raise PermissionError(f"Tài khoản không có quyền: {permission}.")

    def _audit(
        self,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        details: str = "",
    ) -> None:
        if self.actor_id is not None:
            self.audit.record(
                self.actor_id, action, entity_type, entity_id, details
            )
