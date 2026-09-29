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
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.memberships.repository import MembershipRepository
from app.modules.services.repository import ServicesRepository


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
        self.recommendations = RecommendationRepository(self.connection)
        self.memberships = MembershipRepository(self.connection)
        self.services = ServicesRepository(self.connection, self.memberships)
        self.reports = ReportRepository(self.connection)
        self.notifications = NotificationRepository(self.connection)
        self.inventory.seed_catalog()
        self.inventory.seed_feeding_profiles()
        self.services.seed_catalog()
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

                CREATE TABLE IF NOT EXISTS animal_intake_receipts (
                    animal_id INTEGER PRIMARY KEY
                        REFERENCES animals(id) ON DELETE CASCADE,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    received_by TEXT NOT NULL,
                    photo_mime TEXT NOT NULL,
                    photo_data BLOB NOT NULL CHECK (length(photo_data) > 0),
                    confirmation TEXT NOT NULL
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
                    password_changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    must_change_password INTEGER NOT NULL DEFAULT 0
                        CHECK (must_change_password IN (0, 1))
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

                CREATE TABLE IF NOT EXISTS membership_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
                    price REAL NOT NULL CHECK (price >= 0),
                    discount_percent REAL NOT NULL DEFAULT 0
                        CHECK (discount_percent >= 0 AND discount_percent <= 100),
                    points_rate REAL NOT NULL DEFAULT 1 CHECK (points_rate >= 0),
                    benefits TEXT NOT NULL DEFAULT '',
                    max_pets INTEGER NOT NULL DEFAULT 1 CHECK (max_pets > 0),
                    billing_mode TEXT NOT NULL DEFAULT 'MEMBER_DISCOUNT'
                        CHECK (billing_mode IN ('PREPAID_VISITS', 'MEMBER_DISCOUNT', 'RECURRING')),
                    included_visits INTEGER NOT NULL DEFAULT 0 CHECK (included_visits >= 0),
                    service_category TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS memberships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    plan_id INTEGER NOT NULL REFERENCES membership_plans(id) ON DELETE RESTRICT,
                    membership_code TEXT NOT NULL UNIQUE,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('PENDING_PAYMENT', 'ACTIVE', 'EXPIRED', 'SUSPENDED', 'CANCELLED')
                    ),
                    auto_renew INTEGER NOT NULL DEFAULT 0 CHECK (auto_renew IN (0, 1)),
                    renewal_count INTEGER NOT NULL DEFAULT 0 CHECK (renewal_count >= 0),
                    previous_membership_id INTEGER REFERENCES memberships(id) ON DELETE RESTRICT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS membership_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    membership_id INTEGER NOT NULL REFERENCES memberships(id) ON DELETE RESTRICT,
                    card_number TEXT NOT NULL UNIQUE,
                    card_token TEXT NOT NULL UNIQUE,
                    issue_date TEXT NOT NULL,
                    activation_date TEXT,
                    expiry_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('PENDING', 'ACTIVE', 'EXPIRED', 'LOCKED', 'REPLACED', 'CANCELLED')
                    ),
                    replaced_by_card_id INTEGER REFERENCES membership_cards(id) ON DELETE RESTRICT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS membership_card_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL REFERENCES membership_cards(id) ON DELETE RESTRICT,
                    status TEXT NOT NULL,
                    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    note TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    membership_id INTEGER REFERENCES memberships(id) ON DELETE RESTRICT,
                    bill_type TEXT NOT NULL CHECK (
                        bill_type IN ('MEMBERSHIP', 'RENEWAL', 'OTHER')
                    ),
                    subtotal REAL NOT NULL CHECK (subtotal >= 0),
                    discount_amount REAL NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
                    tax_amount REAL NOT NULL DEFAULT 0 CHECK (tax_amount >= 0),
                    service_fee REAL NOT NULL DEFAULT 0 CHECK (service_fee >= 0),
                    total_amount REAL NOT NULL CHECK (total_amount >= 0),
                    currency TEXT NOT NULL DEFAULT 'VND',
                    status TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING', 'PARTIALLY_PAID', 'PAID', 'CANCELLED')),
                    issued_at TEXT NOT NULL,
                    paid_at TEXT,
                    renewal_days INTEGER NOT NULL DEFAULT 0 CHECK (renewal_days >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE RESTRICT,
                    item_name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    discount REAL NOT NULL DEFAULT 0 CHECK (discount >= 0),
                    tax REAL NOT NULL DEFAULT 0 CHECK (tax >= 0),
                    total REAL NOT NULL CHECK (total >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bill_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE RESTRICT,
                    payment_code TEXT NOT NULL UNIQUE,
                    payment_method TEXT NOT NULL CHECK (
                        payment_method IN ('CASH', 'BANK_TRANSFER', 'CARD', 'OTHER')
                    ),
                    amount REAL NOT NULL CHECK (amount > 0),
                    reference TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    paid_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS service_packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    species TEXT NOT NULL DEFAULT 'Chó, Mèo',
                    coat_types TEXT NOT NULL DEFAULT 'ANY',
                    min_weight REAL NOT NULL DEFAULT 0 CHECK (min_weight >= 0),
                    max_weight REAL CHECK (max_weight IS NULL OR max_weight >= min_weight),
                    duration_minutes INTEGER NOT NULL DEFAULT 60 CHECK (duration_minutes > 0),
                    list_price REAL NOT NULL CHECK (list_price >= 0),
                    member_price REAL CHECK (member_price IS NULL OR member_price >= 0),
                    included_weight_kg REAL NOT NULL DEFAULT 0 CHECK (included_weight_kg >= 0),
                    surcharge_per_kg REAL NOT NULL DEFAULT 0 CHECK (surcharge_per_kg >= 0),
                    coat_surcharge REAL NOT NULL DEFAULT 0 CHECK (coat_surcharge >= 0),
                    is_demo INTEGER NOT NULL DEFAULT 1 CHECK (is_demo IN (0, 1)),
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS service_appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_code TEXT NOT NULL UNIQUE,
                    package_id INTEGER NOT NULL REFERENCES service_packages(id) ON DELETE RESTRICT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
                    membership_id INTEGER REFERENCES memberships(id) ON DELETE RESTRICT,
                    pet_name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    weight_kg REAL CHECK (weight_kg IS NULL OR weight_kg >= 0),
                    coat_type TEXT NOT NULL DEFAULT 'Không rõ',
                    scheduled_at TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL DEFAULT 60
                        CHECK (duration_minutes > 0),
                    assigned_staff TEXT NOT NULL DEFAULT '',
                    base_price REAL NOT NULL CHECK (base_price >= 0),
                    surcharge REAL NOT NULL DEFAULT 0 CHECK (surcharge >= 0),
                    discount REAL NOT NULL DEFAULT 0 CHECK (discount >= 0),
                    total_price REAL NOT NULL CHECK (total_price >= 0),
                    status TEXT NOT NULL DEFAULT 'SCHEDULED' CHECK (
                        status IN ('SCHEDULED', 'CHECKED_IN', 'IN_PROGRESS',
                                   'COMPLETED', 'CANCELLED', 'NO_SHOW')
                    ),
                    bill_id INTEGER REFERENCES bills(id) ON DELETE RESTRICT,
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS membership_service_uses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membership_id INTEGER NOT NULL REFERENCES memberships(id) ON DELETE RESTRICT,
                    appointment_id INTEGER NOT NULL UNIQUE
                        REFERENCES service_appointments(id) ON DELETE RESTRICT,
                    cycle_number INTEGER NOT NULL DEFAULT 0 CHECK (cycle_number >= 0),
                    status TEXT NOT NULL CHECK (status IN ('RESERVED', 'USED', 'RELEASED')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_memberships_customer_end
                    ON memberships(customer_id, end_date DESC);
                CREATE INDEX IF NOT EXISTS idx_service_appointments_schedule
                    ON service_appointments(status, scheduled_at);
                CREATE INDEX IF NOT EXISTS idx_service_appointments_customer
                    ON service_appointments(customer_id, scheduled_at DESC);
                CREATE INDEX IF NOT EXISTS idx_service_membership_uses
                    ON membership_service_uses(membership_id, status);
                CREATE INDEX IF NOT EXISTS idx_bills_customer_date
                    ON bills(customer_id, issued_at DESC);
                CREATE INDEX IF NOT EXISTS idx_bill_payments_bill_date
                    ON bill_payments(bill_id, paid_at DESC);

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
                    category TEXT NOT NULL CHECK (
                        category IN ('FOOD', 'MEDICINE', 'SUPPLIES')
                    ),
                    unit TEXT NOT NULL,
                    minimum_stock REAL NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
                    description TEXT NOT NULL DEFAULT '',
                    catalog_category TEXT NOT NULL DEFAULT '',
                    target_species TEXT NOT NULL DEFAULT '',
                    age_group TEXT NOT NULL DEFAULT '',
                    pack_size TEXT NOT NULL DEFAULT '',
                    brand TEXT NOT NULL DEFAULT '',
                    barcode TEXT NOT NULL DEFAULT '',
                    retail_price REAL NOT NULL DEFAULT 0 CHECK (retail_price >= 0),
                    member_price REAL CHECK (member_price IS NULL OR member_price >= 0),
                    promotion_percent REAL NOT NULL DEFAULT 0
                        CHECK (promotion_percent >= 0 AND promotion_percent <= 100),
                    promotion_note TEXT NOT NULL DEFAULT '',
                    ingredients TEXT NOT NULL DEFAULT '',
                    image_path TEXT NOT NULL DEFAULT '',
                    is_demo INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0, 1)),
                    animal_subspecies TEXT NOT NULL DEFAULT '',
                    age_min_months REAL CHECK (age_min_months IS NULL OR age_min_months >= 0),
                    age_max_months REAL CHECK (age_max_months IS NULL OR age_max_months >= 0),
                    age_unit TEXT NOT NULL DEFAULT 'MONTH'
                        CHECK (age_unit IN ('MONTH', 'YEAR', 'LABEL')),
                    life_stage TEXT NOT NULL DEFAULT '',
                    food_category TEXT NOT NULL DEFAULT '',
                    food_type TEXT NOT NULL DEFAULT '',
                    food_subtype TEXT NOT NULL DEFAULT '',
                    breed_size TEXT NOT NULL DEFAULT '',
                    suitable_weight_min REAL CHECK (
                        suitable_weight_min IS NULL OR suitable_weight_min >= 0
                    ),
                    suitable_weight_max REAL CHECK (
                        suitable_weight_max IS NULL OR suitable_weight_max >= 0
                    ),
                    feeding_frequency TEXT NOT NULL DEFAULT 'Theo hướng dẫn sản phẩm',
                    feeding_time TEXT NOT NULL DEFAULT '',
                    serving_size TEXT NOT NULL DEFAULT '',
                    protein_source TEXT NOT NULL DEFAULT '',
                    nutrition_type TEXT NOT NULL DEFAULT '',
                    purpose TEXT NOT NULL DEFAULT '',
                    vitamin_c_content TEXT NOT NULL DEFAULT '',
                    water_level TEXT NOT NULL DEFAULT '',
                    diet_type TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS feeding_age_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    species TEXT NOT NULL,
                    subspecies TEXT NOT NULL DEFAULT '',
                    breed_size TEXT NOT NULL DEFAULT 'ALL',
                    life_stage TEXT NOT NULL,
                    age_min_months REAL CHECK (age_min_months IS NULL OR age_min_months >= 0),
                    age_max_months REAL CHECK (age_max_months IS NULL OR age_max_months >= 0),
                    age_unit TEXT NOT NULL DEFAULT 'MONTH'
                        CHECK (age_unit IN ('MONTH', 'YEAR', 'SPECIES', 'LABEL')),
                    food_category TEXT NOT NULL DEFAULT '',
                    food_type TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE', 'INACTIVE')),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHECK (
                        age_min_months IS NULL OR age_max_months IS NULL
                        OR age_min_months <= age_max_months
                    )
                );

                CREATE TABLE IF NOT EXISTS product_combos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    combo_code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    target_species TEXT NOT NULL DEFAULT '',
                    sale_price REAL NOT NULL CHECK (sale_price >= 0),
                    member_price REAL CHECK (member_price IS NULL OR member_price >= 0),
                    promotion_percent REAL NOT NULL DEFAULT 0
                        CHECK (promotion_percent >= 0 AND promotion_percent <= 100),
                    is_demo INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0, 1)),
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_combo_items (
                    combo_id INTEGER NOT NULL REFERENCES product_combos(id) ON DELETE RESTRICT,
                    item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    PRIMARY KEY (combo_id, item_id)
                );

                CREATE TABLE IF NOT EXISTS sales_product_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    combo_id INTEGER REFERENCES product_combos(id) ON DELETE RESTRICT,
                    item_name TEXT NOT NULL,
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    line_total REAL NOT NULL CHECK (line_total >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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

                CREATE TABLE IF NOT EXISTS product_recommendation_profiles (
                    item_id INTEGER PRIMARY KEY
                        REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    recommendation_category TEXT NOT NULL CHECK (
                        recommendation_category IN (
                            'FOOD', 'HYGIENE', 'ACCESSORY', 'SUPPLEMENT',
                            'TRAINING', 'OTHER', 'VETERINARY'
                        )
                    ),
                    species_tags TEXT NOT NULL DEFAULT '[]',
                    age_groups TEXT NOT NULL DEFAULT '[]',
                    breed_tags TEXT NOT NULL DEFAULT '[]',
                    gender_tags TEXT NOT NULL DEFAULT '[]',
                    needs_tags TEXT NOT NULL DEFAULT '[]',
                    health_tags TEXT NOT NULL DEFAULT '[]',
                    activity_tags TEXT NOT NULL DEFAULT '[]',
                    coat_tags TEXT NOT NULL DEFAULT '[]',
                    environment_tags TEXT NOT NULL DEFAULT '[]',
                    avoid_tags TEXT NOT NULL DEFAULT '[]',
                    minimum_weight REAL CHECK (minimum_weight IS NULL OR minimum_weight >= 0),
                    maximum_weight REAL CHECK (maximum_weight IS NULL OR maximum_weight >= 0),
                    recommendation_price REAL NOT NULL DEFAULT 0
                        CHECK (recommendation_price >= 0),
                    popularity INTEGER NOT NULL DEFAULT 0
                        CHECK (popularity BETWEEN 0 AND 100),
                    note TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHECK (
                        minimum_weight IS NULL OR maximum_weight IS NULL
                        OR minimum_weight <= maximum_weight
                    )
                );

                CREATE TABLE IF NOT EXISTS recommendation_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    item_id INTEGER NOT NULL
                        REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
                    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    event_type TEXT NOT NULL CHECK (
                        event_type IN (
                            'VIEW', 'CLICK', 'SEARCH', 'LIKE', 'ADD_TO_CART',
                            'PURCHASE', 'REVIEW', 'REMOVE_CART'
                        )
                    ),
                    note TEXT NOT NULL DEFAULT '',
                    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS animal_product_preferences (
                    animal_id INTEGER NOT NULL
                        REFERENCES animals(id) ON DELETE CASCADE,
                    item_id INTEGER NOT NULL
                        REFERENCES inventory_items(id) ON DELETE RESTRICT,
                    preference TEXT NOT NULL
                        CHECK (preference IN ('LIKE', 'AVOID')),
                    note TEXT NOT NULL DEFAULT '',
                    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (animal_id, item_id)
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
                CREATE INDEX IF NOT EXISTS idx_recommendation_interactions_pet_date
                    ON recommendation_interactions(animal_id, occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_recommendation_interactions_event
                    ON recommendation_interactions(animal_id, event_type, item_id);
                CREATE INDEX IF NOT EXISTS idx_animal_product_preferences_item
                    ON animal_product_preferences(item_id, preference);
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
        self._migrate_inventory_categories()
        self._migrate_inventory_catalog()
        self._migrate_service_memberships()
        self._migrate_authentication()

    def _migrate_authentication(self) -> None:
        columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(users)")
        }
        if "must_change_password" not in columns:
            with self.connection:
                self.connection.execute(
                    """
                    ALTER TABLE users ADD COLUMN must_change_password
                    INTEGER NOT NULL DEFAULT 0 CHECK (must_change_password IN (0, 1))
                    """
                )

    def _migrate_service_memberships(self) -> None:
        columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(membership_plans)")
        }
        additions = {
            "billing_mode": (
                "TEXT NOT NULL DEFAULT 'MEMBER_DISCOUNT' "
                "CHECK (billing_mode IN ('PREPAID_VISITS', 'MEMBER_DISCOUNT', 'RECURRING'))"
            ),
            "included_visits": "INTEGER NOT NULL DEFAULT 0 CHECK (included_visits >= 0)",
            "service_category": "TEXT NOT NULL DEFAULT ''",
        }
        with self.connection:
            for column, definition in additions.items():
                if column not in columns:
                    self.connection.execute(
                        f"ALTER TABLE membership_plans ADD COLUMN {column} {definition}"
                    )
            appointment_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(service_appointments)"
                )
            }
            if "duration_minutes" not in appointment_columns:
                self.connection.execute(
                    """
                    ALTER TABLE service_appointments ADD COLUMN duration_minutes
                    INTEGER NOT NULL DEFAULT 60 CHECK (duration_minutes > 0)
                    """
                )
            use_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(membership_service_uses)"
                )
            }
            if "cycle_number" not in use_columns:
                self.connection.execute(
                    """
                    ALTER TABLE membership_service_uses ADD COLUMN cycle_number
                    INTEGER NOT NULL DEFAULT 0 CHECK (cycle_number >= 0)
                    """
                )

    def _migrate_inventory_catalog(self) -> None:
        columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(inventory_items)")
        }
        additions = {
            "catalog_category": "TEXT NOT NULL DEFAULT ''",
            "target_species": "TEXT NOT NULL DEFAULT ''",
            "age_group": "TEXT NOT NULL DEFAULT ''",
            "pack_size": "TEXT NOT NULL DEFAULT ''",
            "brand": "TEXT NOT NULL DEFAULT ''",
            "barcode": "TEXT NOT NULL DEFAULT ''",
            "retail_price": "REAL NOT NULL DEFAULT 0 CHECK (retail_price >= 0)",
            "member_price": "REAL CHECK (member_price IS NULL OR member_price >= 0)",
            "promotion_percent": (
                "REAL NOT NULL DEFAULT 0 "
                "CHECK (promotion_percent >= 0 AND promotion_percent <= 100)"
            ),
            "promotion_note": "TEXT NOT NULL DEFAULT ''",
            "ingredients": "TEXT NOT NULL DEFAULT ''",
            "image_path": "TEXT NOT NULL DEFAULT ''",
            "is_demo": "INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0, 1))",
            "animal_subspecies": "TEXT NOT NULL DEFAULT ''",
            "age_min_months": "REAL CHECK (age_min_months IS NULL OR age_min_months >= 0)",
            "age_max_months": "REAL CHECK (age_max_months IS NULL OR age_max_months >= 0)",
            "age_unit": "TEXT NOT NULL DEFAULT 'MONTH'",
            "life_stage": "TEXT NOT NULL DEFAULT ''",
            "food_category": "TEXT NOT NULL DEFAULT ''",
            "food_type": "TEXT NOT NULL DEFAULT ''",
            "food_subtype": "TEXT NOT NULL DEFAULT ''",
            "breed_size": "TEXT NOT NULL DEFAULT ''",
            "suitable_weight_min": (
                "REAL CHECK (suitable_weight_min IS NULL OR suitable_weight_min >= 0)"
            ),
            "suitable_weight_max": (
                "REAL CHECK (suitable_weight_max IS NULL OR suitable_weight_max >= 0)"
            ),
            "feeding_frequency": "TEXT NOT NULL DEFAULT 'Theo hướng dẫn sản phẩm'",
            "feeding_time": "TEXT NOT NULL DEFAULT ''",
            "serving_size": "TEXT NOT NULL DEFAULT ''",
            "protein_source": "TEXT NOT NULL DEFAULT ''",
            "nutrition_type": "TEXT NOT NULL DEFAULT ''",
            "purpose": "TEXT NOT NULL DEFAULT ''",
            "vitamin_c_content": "TEXT NOT NULL DEFAULT ''",
            "water_level": "TEXT NOT NULL DEFAULT ''",
            "diet_type": "TEXT NOT NULL DEFAULT ''",
        }
        with self.connection:
            for column, definition in additions.items():
                if column not in columns:
                    self.connection.execute(
                        f"ALTER TABLE inventory_items ADD COLUMN {column} {definition}"
                    )
            self.connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_items_barcode
                ON inventory_items(barcode) WHERE barcode != ''
                """
            )
            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_inventory_food_filter
                ON inventory_items(target_species, life_stage, food_category, food_type)
                """
            )

    def _migrate_inventory_categories(self) -> None:
        schema = self.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'inventory_items'"
        ).fetchone()
        if schema is None or "SUPPLIES" in schema["sql"]:
            return

        foreign_keys_enabled = bool(
            self.connection.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        self.connection.commit()
        if foreign_keys_enabled:
            self.connection.execute("PRAGMA foreign_keys = OFF")
        try:
            with self.connection:
                self.connection.execute(
                    """
                    CREATE TABLE inventory_items_recommendation_migration (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_code TEXT NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL
                            CHECK (category IN ('FOOD', 'MEDICINE', 'SUPPLIES')),
                        unit TEXT NOT NULL,
                        minimum_stock REAL NOT NULL DEFAULT 0
                            CHECK (minimum_stock >= 0),
                        description TEXT NOT NULL DEFAULT '',
                        is_active INTEGER NOT NULL DEFAULT 1
                            CHECK (is_active IN (0, 1)),
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                self.connection.execute(
                    """
                    INSERT INTO inventory_items_recommendation_migration
                        (id, item_code, name, category, unit, minimum_stock,
                         description, is_active, created_at, updated_at)
                    SELECT id, item_code, name, category, unit, minimum_stock,
                           description, is_active, created_at, updated_at
                    FROM inventory_items
                    """
                )
                self.connection.execute("DROP TABLE inventory_items")
                self.connection.execute(
                    """
                    ALTER TABLE inventory_items_recommendation_migration
                    RENAME TO inventory_items
                    """
                )
        finally:
            if foreign_keys_enabled:
                self.connection.execute("PRAGMA foreign_keys = ON")
        if foreign_keys_enabled:
            violations = self.connection.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise sqlite3.IntegrityError(
                    "Dữ liệu tồn kho không vượt qua kiểm tra khóa ngoại sau migration."
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

    def create_product_sales_order(self, values: dict[str, Any]) -> int:
        self._require_permission("sales.manage")
        result = self.sales.create_product_order(values)
        self._audit(
            "CREATE_PRODUCT_ORDER",
            "sales_order",
            result,
            f"customer_id={values['customer_id']}; "
            f"products={len(values.get('product_lines', []))}; "
            f"combos={len(values.get('combo_lines', []))}",
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
        received_by = self.current_actor_name()
        result = self.imports.add_animal_to_batch(
            batch_id,
            {**values, "received_by": values.get("received_by") or received_by},
        )
        self._audit(
            "INTAKE_RECEIVED",
            "animal",
            result,
            f"batch_id={batch_id}; photo_receipt=confirmed",
        )
        return result

    def get_intake_receipt(self, animal_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT animal_id, received_at, received_by, photo_mime, photo_data,
                   confirmation
            FROM animal_intake_receipts WHERE animal_id = ?
            """,
            (animal_id,),
        ).fetchone()

    def current_actor_name(self) -> str:
        if self.actor_id is None:
            return ""
        row = self.connection.execute(
            "SELECT display_name FROM users WHERE id = ?", (self.actor_id,)
        ).fetchone()
        return row["display_name"] if row else ""

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

    def list_membership_plans(self, include_inactive: bool = True) -> list[sqlite3.Row]:
        self._require_permission("membership.view")
        return self.memberships.list_plans(include_inactive)

    def save_membership_plan(
        self, values: dict[str, Any], plan_id: int | None = None
    ) -> int:
        self._require_permission("membership.manage")
        result = self.memberships.save_plan(values, plan_id)
        self._audit(
            "UPDATE" if plan_id is not None else "CREATE",
            "membership_plan",
            result,
        )
        return result

    def list_memberships(self, search: str = "") -> list[sqlite3.Row]:
        self._require_permission("membership.view")
        return self.memberships.list_memberships(search)

    def create_membership(self, customer_id: int, plan_id: int) -> int:
        self._require_permission("membership.manage")
        result = self.memberships.create_membership(customer_id, plan_id)
        self._audit("CREATE", "membership", result, f"customer_id={customer_id}; plan_id={plan_id}")
        return result

    def create_membership_renewal(self, membership_id: int) -> int:
        self._require_permission("membership.manage")
        result = self.memberships.create_renewal_bill(membership_id)
        self._audit("CREATE_RENEWAL_BILL", "membership", membership_id, f"bill_id={result}")
        return result

    def list_membership_bills(self, search: str = "") -> list[sqlite3.Row]:
        self._require_permission("membership.view")
        return self.memberships.list_bills(search)

    def add_membership_bill_payment(
        self, bill_id: int, values: dict[str, Any]
    ) -> int:
        self._require_permission("membership.manage")
        result = self.memberships.add_bill_payment(bill_id, values)
        self._audit(
            "RECORD_PAYMENT",
            "membership_bill",
            bill_id,
            f"payment_id={result}; amount={values.get('amount')}",
        )
        return result

    def list_membership_bill_payments(self, bill_id: int) -> list[sqlite3.Row]:
        self._require_permission("membership.view")
        return self.memberships.list_bill_payments(bill_id)

    def verify_membership_card(self, token: str) -> sqlite3.Row | None:
        self._require_permission("membership.view")
        if not token.strip():
            raise ValueError("Mã xác minh thẻ không được để trống.")
        return self.memberships.verify_card(token.strip())

    def list_service_packages(
        self, search: str = "", include_inactive: bool = True
    ) -> list[sqlite3.Row]:
        self._require_permission("services.view")
        return self.services.list_packages(search, include_inactive)

    def save_service_package(
        self, values: dict[str, Any], package_id: int | None = None
    ) -> int:
        self._require_permission("services.catalog.manage")
        result = self.services.save_package(values, package_id)
        self._audit(
            "UPDATE" if package_id is not None else "CREATE",
            "service_package",
            result,
        )
        return result

    def get_service_quote(
        self,
        package_id: int,
        species: str,
        weight_kg: float | None = None,
        coat_type: str = "Không rõ",
        membership_id: int | None = None,
    ) -> dict[str, Any]:
        self._require_permission("services.view")
        return self.services.quote(
            package_id, species, weight_kg, coat_type, membership_id
        )

    def list_customer_service_memberships(
        self, customer_id: int
    ) -> list[sqlite3.Row]:
        self._require_permission("services.view")
        return self.services.customer_memberships(customer_id)

    def list_service_staff(self) -> list[str]:
        self._require_permission("services.view")
        return [
            row["display_name"]
            for row in self.connection.execute(
                """
                SELECT display_name FROM users
                WHERE is_active = 1 AND role IN ('ADMIN', 'MANAGER', 'CAREGIVER')
                ORDER BY display_name COLLATE NOCASE
                """
            ).fetchall()
        ]

    def create_service_appointment(self, values: dict[str, Any]) -> int:
        self._require_permission("services.manage")
        result = self.services.create_appointment(values)
        self._audit(
            "CREATE",
            "service_appointment",
            result,
            f"customer_id={values.get('customer_id')}; package_id={values.get('package_id')}",
        )
        return result

    def list_service_appointments(self, search: str = "") -> list[sqlite3.Row]:
        self._require_permission("services.view")
        return self.services.list_appointments(search)

    def reschedule_service_appointment(
        self, appointment_id: int, scheduled_at: str
    ) -> None:
        self._require_permission("services.manage")
        self.services.reschedule_appointment(appointment_id, scheduled_at)
        self._audit(
            "RESCHEDULE",
            "service_appointment",
            appointment_id,
            f"scheduled_at={scheduled_at}",
        )

    def update_service_appointment_status(
        self, appointment_id: int, status: str
    ) -> None:
        self._require_permission("services.manage")
        self.services.update_appointment_status(appointment_id, status)
        self._audit(
            "UPDATE_STATUS",
            "service_appointment",
            appointment_id,
            f"status={status}",
        )

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

    def list_order_product_items(self, order_id: int) -> list[sqlite3.Row]:
        return self.sales.list_order_product_items(order_id)

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

    def list_inventory_combos(self, active_only: bool = False) -> list[sqlite3.Row]:
        self._require_permission("inventory.view")
        return self.inventory.list_combos(active_only)

    def list_inventory_combo_items(self, combo_id: int) -> list[sqlite3.Row]:
        self._require_permission("inventory.view")
        return self.inventory.list_combo_items(combo_id)

    def save_inventory_combo(
        self,
        values: dict[str, Any],
        components: list[dict[str, Any]],
        combo_id: int | None = None,
    ) -> int:
        self._require_permission("inventory.manage")
        result = self.inventory.save_combo(values, components, combo_id)
        self._audit(
            "UPDATE" if combo_id is not None else "CREATE",
            "product_combo",
            result,
        )
        return result

    def list_saleable_products(self, customer_id: int) -> list[dict[str, Any]]:
        self._require_permission("sales.view")
        return self.sales.list_saleable_products(customer_id)

    def list_saleable_combos(self, customer_id: int) -> list[dict[str, Any]]:
        self._require_permission("sales.view")
        return self.sales.list_saleable_combos(customer_id)

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

    def list_feeding_age_rules(
        self, active_only: bool = True
    ) -> list[sqlite3.Row]:
        self._require_permission("inventory.view")
        return self.inventory.list_age_rules(active_only)

    def save_feeding_age_rule(
        self, values: dict[str, Any], rule_id: int | None = None
    ) -> int:
        self._require_permission("inventory.manage")
        result = self.inventory.save_age_rule(values, rule_id)
        self._audit(
            "UPDATE" if rule_id is not None else "CREATE",
            "feeding_age_rule",
            result,
        )
        return result

    def get_feeding_recommendations(
        self, animal_id: int, water_level: str = "", diet_type: str = ""
    ) -> dict[str, Any]:
        self._require_permission("inventory.view")
        animal = self.animals.get_animal(animal_id)
        if animal is None:
            raise ValueError("Không tìm thấy hồ sơ động vật.")
        return self.inventory.recommend_feeding_products(
            animal, water_level, diet_type
        )

    def set_inventory_item_active(self, item_id: int, active: bool) -> None:
        self._require_permission("inventory.manage")
        self.inventory.set_item_active(item_id, active)
        self._audit(
            "ACTIVATE" if active else "DEACTIVATE", "inventory_item", item_id
        )

    def list_recommendation_products(self) -> list[sqlite3.Row]:
        self._require_permission("inventory.view")
        return self.recommendations.list_products()

    def get_recommendation_profile(
        self, item_id: int
    ) -> sqlite3.Row | None:
        self._require_permission("inventory.view")
        return self.recommendations.get_profile(item_id)

    def save_recommendation_profile(
        self, item_id: int, values: dict[str, Any]
    ) -> None:
        self._require_permission("inventory.manage")
        self.recommendations.save_profile(item_id, values)
        self._audit("UPDATE_RECOMMENDATION_PROFILE", "inventory_item", item_id)

    def delete_recommendation_profile(self, item_id: int) -> None:
        self._require_permission("inventory.manage")
        self.recommendations.delete_profile(item_id)
        self._audit("DELETE_RECOMMENDATION_PROFILE", "inventory_item", item_id)

    def list_recommendation_interactions(
        self, animal_id: int, customer_id: int | None = None
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.recommendations.list_interactions(animal_id, customer_id)

    def list_recommendation_peer_interactions(
        self, animal_id: int, customer_id: int | None = None
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.recommendations.list_peer_interactions(animal_id, customer_id)

    def record_recommendation_interaction(
        self,
        animal_id: int,
        item_id: int,
        event_type: str,
        customer_id: int | None = None,
        note: str = "",
    ) -> int:
        self._require_permission("inventory.view")
        result = self.recommendations.record_interaction(
            animal_id, item_id, event_type, self.actor_id, customer_id, note
        )
        self._audit(
            "RECOMMENDATION_INTERACTION",
            "inventory_item",
            item_id,
            f"animal_id={animal_id}; event={event_type}; customer_id={customer_id}",
        )
        return result

    def list_animal_product_preferences(
        self, animal_id: int
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.recommendations.list_animal_product_preferences(animal_id)

    def save_animal_product_preference(
        self,
        animal_id: int,
        item_id: int,
        preference: str,
        note: str = "",
    ) -> None:
        self._require_permission("inventory.view")
        self.recommendations.save_animal_product_preference(
            animal_id,
            item_id,
            preference,
            self.actor_id,
            note,
        )
        self._audit(
            "SAVE_PET_PRODUCT_PREFERENCE",
            "animal_product_preference",
            item_id,
            f"animal_id={animal_id}; preference={preference}",
        )

    def delete_animal_product_preference(
        self, animal_id: int, item_id: int
    ) -> None:
        self._require_permission("inventory.view")
        self.recommendations.delete_animal_product_preference(animal_id, item_id)
        self._audit(
            "DELETE_PET_PRODUCT_PREFERENCE",
            "animal_product_preference",
            item_id,
            f"animal_id={animal_id}",
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

    def create_default_admin(self) -> int:
        user_id = self.auth.create_default_admin()
        self.audit.record(
            user_id,
            "INITIAL_ADMIN_DEFAULT",
            "user",
            user_id,
            "Default credentials; password change required at first login",
        )
        return user_id

    def reset_admin_login(self, username: str = "admin") -> int:
        user_id = self.auth.reset_admin_password(username)
        self.audit.record(
            None,
            "ADMIN_PASSWORD_RESET",
            "user",
            user_id,
            "Local recovery reset password to temporary default; change required",
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
