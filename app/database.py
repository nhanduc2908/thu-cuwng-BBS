from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import secrets
import sqlite3
from typing import Any

DEFAULT_DATABASE_PATH = Path.home() / "AppData" / "Local" / "PetStoreManagement" / "pet_store.db"


def get_db_connection(path: str | Path | None = None) -> sqlite3.Connection:
    target = Path(path) if path is not None else DEFAULT_DATABASE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


from app.modules.animals.constants import (
    ANIMAL_PROFILE_FIELDS,
    ANIMAL_STATUSES,
)
from app.modules.animals.repository import AnimalRepository, BreedRepository
from app.modules.audit.repository import AuditRepository
from app.modules.auth.repository import AuthRepository
from app.modules.auth.constants import ROLE_PERMISSIONS
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
    def __init__(self, path: str | Path, *, initialize: bool = True) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        if initialize:
            self._create_tables()
        self.auth = AuthRepository(self.connection)
        self.audit = AuditRepository(self.connection)
        self.animals = AnimalRepository(self.connection)
        self.breeds = BreedRepository(self.connection)
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
        self.actor_id: int | None = None
        if initialize:
            self._seed_health_catalogs()
            self.breeds.seed_default_catalog()
            self.inventory.seed_catalog()
            self.inventory.seed_feeding_profiles()
            self.services.seed_catalog()

    def _seed_health_catalogs(self) -> None:
        default_diseases = [
            ("DOG", "DOG_PARVOVIRUS", "Parvovirus", "INFECTIOUS", "HIGH", "Bệnh lây nhiễm nguy hiểm ở chó con, gây nôn mửa và tiêu chảy.", "Nôn, tiêu chảy, mất nước, sốt", "Hỗ trợ hồi phục, thuốc chống nôn, truyền dịch nếu cần", "Tiêm phòng đầy đủ, vệ sinh môi trường, tránh tiếp xúc với động vật bệnh"),
            ("DOG", "DOG_DISTEMPER", "Distemper", "INFECTIOUS", "HIGH", "Nhiễm virus gây viêm hô hấp, thần kinh và tiêu hóa.", "Ho, chảy nước mắt, sốt, co giật", "Điều trị triệu chứng, thuốc kháng virus theo chỉ định", "Tiêm phòng đúng lịch"),
            ("DOG", "DOG_KENNEL_COUGH", "Kennel Cough", "RESPIRATORY", "MEDIUM", "Cúm chó, ho kéo dài do nhiễm đường hô hấp trên.", "Ho khan, khó thở, ho tăng khi kích thích", "Tái tạo môi trường, thuốc hỗ trợ hô hấp", "Tiêm phòng kháng viêm đường hô hấp"),
            ("DOG", "DOG_SKIN_ALLERGY", "Dị ứng da", "DERMATOLOGY", "MEDIUM", "Phản ứng da do thức ăn hoặc môi trường.", "Ngứa, đỏ da, rụng lông", "Kiểm soát dị nguyên, thuốc kháng viêm", "Giới hạn dị nguyên và kiểm tra thức ăn"),
            ("CAT", "CAT_FELINE_URI", "Viêm đường hô hấp mèo", "RESPIRATORY", "MEDIUM", "Bệnh đường hô hấp phổ biến ở mèo.", "Hắt hơi, chảy nước mũi, ho", "Vệ sinh mắt/mũi, hỗ trợ điều trị", "Tránh tiếp xúc với mèo bệnh"),
            ("CAT", "CAT_FELV", "Feline Leukemia", "INFECTIOUS", "HIGH", "Bệnh nguy hiểm ở mèo gây suy giảm miễn dịch.", "Sụt cân, sốt, viêm nhiễm", "Theo dõi và hỗ trợ điều trị", "Tiêm phòng và cách ly mèo mới"),
            ("CAT", "CAT_SKIN_ALLERGY", "Dị ứng da mèo", "DERMATOLOGY", "MEDIUM", "Dị ứng thức ăn hoặc môi trường.", "Ngứa, da khô, gãi nhiều", "Thay đổi thức ăn, thuốc hỗ trợ", "Kiểm soát dị nguyên"),
        ]

        default_schedules = [
            ("DOG", "Dại", "PUPPY", "2-4 tháng", 3, 12, "Khuyến nghị tiêm dại theo quy định địa phương."),
            ("DOG", "Parvovirus", "PUPPY", "6-8 tuần", 3, 12, "Lặp lại theo lịch booster."),
            ("DOG", "Canine Distemper", "PUPPY", "6-8 tuần", 3, 12, "Tiêm nhắc lại sau 12 tháng."),
            ("DOG", "Leptospirosis", "ADULT", "12 tháng", 1, 12, "Nên chủ động cho chó ở vùng ẩm hoặc làm việc ngoài trời."),
            ("CAT", "Panleukopenia", "KITTEN", "8-12 tuần", 2, 12, "Tiêm nhắc lai sau 1 năm."),
            ("CAT", "Feline Calicivirus", "KITTEN", "8-12 tuần", 2, 12, "Bảo vệ đường hô hấp và da."),
            ("CAT", "Feline Herpesvirus", "KITTEN", "8-12 tuần", 2, 12, "Theo dõi nếu mèo có chảy nước mắt."),
        ]

        with self.connection:
            for item in default_diseases:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO disease_catalog
                        (species, disease_code, disease_name, category, severity, description, symptoms, treatment, prevention)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    item,
                )
            for item in default_schedules:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO vaccination_schedules
                        (species, vaccine_name, schedule_stage, recommended_months, dose_count, booster_interval_months, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    item,
                )

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

                CREATE TABLE IF NOT EXISTS breed_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species TEXT NOT NULL,
                    breed_name TEXT NOT NULL,
                    breed_name_en TEXT NOT NULL,
                    origin_country TEXT NOT NULL DEFAULT '',
                    origin_region TEXT NOT NULL DEFAULT '',
                    climate TEXT NOT NULL DEFAULT '',
                    suitable_environment TEXT NOT NULL DEFAULT '',
                    exercise_level TEXT NOT NULL DEFAULT '',
                    activity_level TEXT NOT NULL DEFAULT '',
                    energy_level TEXT NOT NULL DEFAULT '',
                    protein_preferences TEXT NOT NULL DEFAULT '',
                    texture_preferences TEXT NOT NULL DEFAULT '',
                    flavor_preferences TEXT NOT NULL DEFAULT '',
                    treat_preferences TEXT NOT NULL DEFAULT '',
                    heat_tolerance TEXT NOT NULL DEFAULT '',
                    cold_tolerance TEXT NOT NULL DEFAULT '',
                    size TEXT NOT NULL DEFAULT '',
                    adult_weight_kg TEXT NOT NULL DEFAULT '',
                    lifespan_years TEXT NOT NULL DEFAULT '',
                    suitable_home TEXT NOT NULL DEFAULT '',
                    exercise_requirement TEXT NOT NULL DEFAULT '',
                    preferred_home TEXT NOT NULL DEFAULT '',
                    temperature_range TEXT NOT NULL DEFAULT '',
                    UNIQUE (species, breed_name)
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

                CREATE TABLE IF NOT EXISTS disease_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species TEXT NOT NULL,
                    disease_code TEXT NOT NULL UNIQUE,
                    disease_name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'GENERAL',
                    severity TEXT NOT NULL DEFAULT 'MEDIUM'
                        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
                    description TEXT NOT NULL DEFAULT '',
                    symptoms TEXT NOT NULL DEFAULT '',
                    treatment TEXT NOT NULL DEFAULT '',
                    prevention TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS vaccination_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species TEXT NOT NULL,
                    vaccine_name TEXT NOT NULL,
                    schedule_stage TEXT NOT NULL DEFAULT 'PUPPY',
                    recommended_months TEXT NOT NULL DEFAULT '0-12',
                    dose_count INTEGER NOT NULL DEFAULT 1,
                    booster_interval_months INTEGER NOT NULL DEFAULT 12,
                    notes TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (species, vaccine_name, schedule_stage)
                );

                CREATE TABLE IF NOT EXISTS vaccination_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE RESTRICT,
                    vaccine_name TEXT NOT NULL,
                    administered_at TEXT NOT NULL,
                    next_due_at TEXT NOT NULL DEFAULT '',
                    dose_number INTEGER NOT NULL DEFAULT 1,
                    veterinarian TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'COMPLETED'
                        CHECK (status IN ('COMPLETED', 'SCHEDULED', 'OVERDUE', 'CANCELLED')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
                        role IN (
                            'ADMIN', 'MANAGER', 'VETERINARIAN', 'CAREGIVER', 'SALES',
                            'INVENTORY_MANAGER', 'SERVICE_COORDINATOR',
                            'CUSTOMER_SUPPORT', 'REPORT_ANALYST', 'AUDITOR'
                        )
                    ),
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    password_changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    must_change_password INTEGER NOT NULL DEFAULT 0
                        CHECK (must_change_password IN (0, 1)),
                    sales_approver INTEGER NOT NULL DEFAULT 0
                        CHECK (sales_approver IN (0, 1))
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

                CREATE TABLE IF NOT EXISTS pet_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL DEFAULT 'Chó',
                    breed_name TEXT NOT NULL DEFAULT '',
                    breed_profile_id INTEGER REFERENCES breed_profiles(id) ON DELETE SET NULL,
                    birth_date TEXT NOT NULL DEFAULT '',
                    sex TEXT NOT NULL DEFAULT 'Chưa rõ'
                        CHECK (sex IN ('Đực', 'Cái', 'Chưa rõ')),
                    color TEXT NOT NULL DEFAULT '',
                    weight_kg REAL CHECK (weight_kg IS NULL OR weight_kg >= 0),
                    activity_level TEXT NOT NULL DEFAULT 'Trung bình',
                    environment_type TEXT NOT NULL DEFAULT 'Trong nhà',
                    body_condition TEXT NOT NULL DEFAULT 'Bình thường',
                    health_status TEXT NOT NULL DEFAULT 'Bình thường',
                    microchip_id TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS customer_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    pet_id INTEGER REFERENCES pet_profiles(id) ON DELETE CASCADE,
                    source TEXT NOT NULL DEFAULT 'WEB'
                        CHECK (source IN ('WEB', 'APP', 'STAFF', 'CALL', 'OTHER')),
                    channel TEXT NOT NULL DEFAULT 'GENERAL'
                        CHECK (channel IN ('GENERAL', 'SALE', 'SERVICE', 'HEALTH', 'FEEDING', 'OTHER')),
                    rating INTEGER NOT NULL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
                    title TEXT NOT NULL DEFAULT '',
                    message TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
                    pet_id INTEGER REFERENCES pet_profiles(id) ON DELETE SET NULL,
                    request_type TEXT NOT NULL DEFAULT 'PRODUCT_RECOMMENDATION',
                    request_context TEXT NOT NULL DEFAULT '{}',
                    status TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL REFERENCES recommendation_requests(id) ON DELETE CASCADE,
                    result_type TEXT NOT NULL DEFAULT 'PRODUCT_PACKAGE'
                        CHECK (result_type IN ('PRODUCT_PACKAGE', 'SERVICE_PACKAGE', 'HEALTH_PLAN', 'COMBO')),
                    result_payload TEXT NOT NULL DEFAULT '{}',
                    score REAL NOT NULL DEFAULT 0,
                    ranked_position INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_result_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL REFERENCES recommendation_results(id) ON DELETE CASCADE,
                    item_type TEXT NOT NULL DEFAULT 'PRODUCT'
                        CHECK (item_type IN ('PRODUCT', 'SERVICE', 'FOOD', 'SUPPLEMENT', 'OTHER')),
                    item_id INTEGER,
                    item_name TEXT NOT NULL DEFAULT '',
                    score REAL NOT NULL DEFAULT 0,
                    reason TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species TEXT NOT NULL,
                    brand TEXT NOT NULL DEFAULT '',
                    product_name TEXT NOT NULL,
                    food_type TEXT NOT NULL DEFAULT 'DRY',
                    life_stage TEXT NOT NULL DEFAULT 'ADULT',
                    breed_size TEXT NOT NULL DEFAULT '',
                    target_weight_kg REAL,
                    product_code TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_nutrition (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    calories_kcal_per_kg REAL,
                    protein_percent REAL,
                    fat_percent REAL,
                    carbohydrate_percent REAL,
                    fiber_percent REAL,
                    moisture_percent REAL,
                    ash_percent REAL,
                    energy_density REAL,
                    omega_3 REAL,
                    omega_6 REAL,
                    taurine REAL,
                    calcium REAL,
                    phosphorus REAL,
                    sodium REAL,
                    potassium REAL,
                    zinc REAL,
                    iron REAL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    ingredient_name TEXT NOT NULL,
                    ingredient_group TEXT NOT NULL DEFAULT 'PROTEIN',
                    percentage REAL,
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_allergens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    allergen_name TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT 'MEDIUM'
                        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_life_stage_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    life_stage TEXT NOT NULL,
                    age_min_months REAL,
                    age_max_months REAL,
                    target_weight_kg REAL,
                    recommendation TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_species_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    species TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS food_health_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER NOT NULL REFERENCES food_catalog(id) ON DELETE CASCADE,
                    condition_name TEXT NOT NULL,
                    recommended INTEGER NOT NULL DEFAULT 0 CHECK (recommended IN (0, 1)),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS nutrition_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_id INTEGER REFERENCES pet_profiles(id) ON DELETE CASCADE,
                    species TEXT NOT NULL,
                    breed_name TEXT NOT NULL DEFAULT '',
                    age_months INTEGER,
                    weight_kg REAL,
                    activity_level TEXT NOT NULL DEFAULT 'MEDIUM',
                    body_condition TEXT NOT NULL DEFAULT 'NORMAL',
                    protein_level TEXT NOT NULL DEFAULT 'MODERATE',
                    fat_level TEXT NOT NULL DEFAULT 'MODERATE',
                    fiber_level TEXT NOT NULL DEFAULT 'MODERATE',
                    omega_3_required INTEGER NOT NULL DEFAULT 0 CHECK (omega_3_required IN (0, 1)),
                    energy_level TEXT NOT NULL DEFAULT 'MODERATE',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_model_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL DEFAULT 'v1',
                    status TEXT NOT NULL DEFAULT 'DRAFT'
                        CHECK (status IN ('DRAFT', 'EVALUATING', 'APPROVED', 'REJECTED', 'ARCHIVED')),
                    metric_snapshot TEXT NOT NULL DEFAULT '{}',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_model_deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    environment TEXT NOT NULL DEFAULT 'staging'
                        CHECK (environment IN ('staging', 'production', 'shadow', 'rollback')),
                    deployed_by TEXT NOT NULL DEFAULT 'system',
                    status TEXT NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE', 'INACTIVE', 'ROLLED_BACK', 'FAILED')),
                    deployed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_governance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    policy_state TEXT NOT NULL DEFAULT '{}',
                    approved INTEGER NOT NULL DEFAULT 0 CHECK (approved IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendation_feedback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER REFERENCES recommendation_requests(id) ON DELETE SET NULL,
                    item_id INTEGER,
                    event_type TEXT NOT NULL DEFAULT 'RATING'
                        CHECK (event_type IN ('RATING', 'PURCHASE', 'BOOKING', 'RETURN', 'REJECTED', 'LIKE')),
                    score REAL NOT NULL DEFAULT 0,
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
                    paid_at TEXT,
                    inventory_fulfilled_at TEXT
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

                CREATE TABLE IF NOT EXISTS sales_approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_code TEXT NOT NULL UNIQUE,
                    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
                    action_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
                    requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
                    reviewed_at TEXT,
                    decision_note TEXT NOT NULL DEFAULT '',
                    result_json TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_sales_approval_queue
                    ON sales_approval_requests(status, requested_at DESC, id DESC);

                CREATE TABLE IF NOT EXISTS store_slips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slip_code TEXT NOT NULL UNIQUE,
                    slip_type TEXT NOT NULL,
                    linked_order_id INTEGER REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    payload_json TEXT NOT NULL,
                    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_store_slips_type_created
                    ON store_slips(slip_type, created_at DESC);

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

                CREATE TABLE IF NOT EXISTS storefront_order_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_code TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    address TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    items_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'NEW'
                        CHECK (status IN ('NEW', 'CONTACTED', 'CLOSED')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sales_order_id INTEGER REFERENCES sales_orders(id) ON DELETE RESTRICT,
                    client_request_id TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_storefront_order_requests_created
                    ON storefront_order_requests(created_at DESC, id DESC);

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

                CREATE TABLE IF NOT EXISTS web_dataset_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id TEXT NOT NULL,
                    source_key TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    is_archived INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0, 1)),
                    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    archived_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (module_id, source_key)
                );

                CREATE TABLE IF NOT EXISTS customer_portal_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING', 'ACTIVE', 'REJECTED')),
                    customer_id INTEGER UNIQUE REFERENCES customers(id) ON DELETE RESTRICT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    approved_at TEXT,
                    reviewed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS customer_portal_invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    token_hash TEXT NOT NULL UNIQUE,
                    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT NOT NULL,
                    redeemed_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_audit_logs_occurred
                    ON audit_logs(occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_logs_actor
                    ON audit_logs(actor_id, occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_pet_profiles_customer
                    ON pet_profiles(customer_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_customer_feedback_pet
                    ON customer_feedback(pet_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_recommendation_requests_customer
                    ON recommendation_requests(customer_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_recommendation_results_request
                    ON recommendation_results(request_id, ranked_position);

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
                CREATE INDEX IF NOT EXISTS idx_web_dataset_records_module
                    ON web_dataset_records(module_id, is_archived, id);
                CREATE INDEX IF NOT EXISTS idx_customer_portal_invites_customer
                    ON customer_portal_invites(customer_id, expires_at, redeemed_at);

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
            customer_account_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(customer_portal_accounts)"
                )
            }
            if "reviewed_at" not in customer_account_columns:
                self.connection.execute(
                    "ALTER TABLE customer_portal_accounts ADD COLUMN reviewed_at TEXT"
                )
            sales_order_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(sales_orders)"
                )
            }
            if "inventory_fulfilled_at" not in sales_order_columns:
                self.connection.execute(
                    "ALTER TABLE sales_orders ADD COLUMN inventory_fulfilled_at TEXT"
                )
            inventory_item_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(inventory_items)"
                )
            }
            if "storefront_auto_inactive" not in inventory_item_columns:
                self.connection.execute(
                    "ALTER TABLE inventory_items ADD COLUMN "
                    "storefront_auto_inactive INTEGER NOT NULL DEFAULT 0"
                )
            combo_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(product_combos)"
                )
            }
            if "storefront_auto_inactive" not in combo_columns:
                self.connection.execute(
                    "ALTER TABLE product_combos ADD COLUMN "
                    "storefront_auto_inactive INTEGER NOT NULL DEFAULT 0"
                )
            storefront_request_columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(storefront_order_requests)"
                )
            }
            if "sales_order_id" not in storefront_request_columns:
                self.connection.execute(
                    "ALTER TABLE storefront_order_requests "
                    "ADD COLUMN sales_order_id INTEGER "
                    "REFERENCES sales_orders(id) ON DELETE RESTRICT"
                )
            if "client_request_id" not in storefront_request_columns:
                self.connection.execute(
                    "ALTER TABLE storefront_order_requests "
                    "ADD COLUMN client_request_id TEXT"
                )
            self.connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_storefront_request_idempotency
                ON storefront_order_requests(client_request_id)
                WHERE client_request_id IS NOT NULL
                """
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
        self._migrate_sales_approver()
        self._migrate_user_roles()

    def _migrate_sales_approver(self) -> None:
        columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(users)")
        }
        if "sales_approver" not in columns:
            with self.connection:
                self.connection.execute(
                    "ALTER TABLE users ADD COLUMN sales_approver INTEGER NOT NULL "
                    "DEFAULT 0 CHECK (sales_approver IN (0, 1))"
                )

    def _migrate_user_roles(self) -> None:
        table = self.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone()
        if table is None or table["sql"] is None:
            return
        if all(role in table["sql"] for role in ROLE_PERMISSIONS):
            return

        role_values = ", ".join(f"'{role}'" for role in ROLE_PERMISSIONS)
        self.connection.commit()
        self.connection.execute("PRAGMA foreign_keys = OFF")
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            self.connection.execute(
                f"""
                CREATE TABLE users_role_migration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ({role_values})),
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    password_changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    must_change_password INTEGER NOT NULL DEFAULT 0
                        CHECK (must_change_password IN (0, 1)),
                    sales_approver INTEGER NOT NULL DEFAULT 0
                        CHECK (sales_approver IN (0, 1))
                )
                """
            )
            self.connection.execute(
                """
                INSERT INTO users_role_migration
                    (id, username, display_name, password_salt, password_hash,
                     role, is_active, created_at, password_changed_at,
                     must_change_password, sales_approver)
                SELECT id, username, display_name, password_salt, password_hash,
                       role, is_active, created_at, password_changed_at,
                       must_change_password, sales_approver
                FROM users
                """
            )
            self.connection.execute("DROP TABLE users")
            self.connection.execute(
                "ALTER TABLE users_role_migration RENAME TO users"
            )
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        finally:
            self.connection.execute("PRAGMA foreign_keys = ON")

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

    def list_disease_catalog(self, species: str | None = None) -> list[sqlite3.Row]:
        return self.health.list_disease_catalog(species)

    def add_disease_catalog_entry(self, values: dict[str, Any]) -> int:
        self._require_permission("health.manage")
        result = self.health.add_disease_catalog_entry(values)
        self._audit("CREATE", "disease_catalog", result)
        return result

    def list_vaccination_schedules(self, species: str | None = None) -> list[sqlite3.Row]:
        return self.health.list_vaccination_schedules(species)

    def add_vaccination_schedule(self, values: dict[str, Any]) -> int:
        self._require_permission("health.manage")
        result = self.health.add_vaccination_schedule(values)
        self._audit("CREATE", "vaccination_schedule", result)
        return result

    def list_vaccination_records(self, animal_id: int | None = None) -> list[sqlite3.Row]:
        return self.health.list_vaccination_records(animal_id)

    def add_vaccination_record(self, values: dict[str, Any]) -> int:
        self._require_permission("health.manage")
        result = self.health.add_vaccination_record(values)
        self._audit("CREATE", "vaccination_record", result)
        return result

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

    def list_pets(self, customer_id: int | None = None) -> list[sqlite3.Row]:
        return self.customers.list_pets(customer_id)

    def get_pet(self, pet_id: int) -> sqlite3.Row | None:
        return self.customers.get_pet(pet_id)

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

    def create_storefront_order_request(self, values: dict[str, Any]) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO storefront_order_requests
                    (request_code, customer_name, customer_phone, address, note, items_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    values["request_code"],
                    values["customer_name"],
                    values["customer_phone"],
                    values.get("address", ""),
                    values.get("note", ""),
                    values["items_json"],
                ),
            )
            return int(cursor.lastrowid)

    def list_storefront_order_requests(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT r.id, r.request_code, r.customer_name, r.customer_phone, r.address,
                   r.note, r.items_json, r.status, r.created_at, r.sales_order_id,
                   so.order_code AS sales_order_code, so.status AS sales_order_status,
                   so.total_amount AS sales_order_total,
                   so.inventory_fulfilled_at
            FROM storefront_order_requests r
            LEFT JOIN sales_orders so ON so.id = r.sales_order_id
            ORDER BY r.created_at DESC, r.id DESC
            """
        ).fetchall()

    def create_storefront_sales_order(self, values: dict[str, Any]) -> dict[str, Any]:
        """Create an unpaid storefront sale and immediately issue its stock."""
        request_code = str(values["request_code"]).strip()
        client_request_id = str(values.get("client_request_id", "")).strip()
        customer_name = str(values["customer_name"]).strip()
        customer_phone = str(values["customer_phone"]).strip()
        items = values["items"]
        if (
            not request_code
            or not client_request_id
            or not customer_name
            or not customer_phone
        ):
            raise ValueError("Thiếu thông tin yêu cầu đặt hàng.")
        if not isinstance(items, list) or not items:
            raise ValueError("Yêu cầu phải có ít nhất một sản phẩm.")

        self.connection.execute("BEGIN IMMEDIATE")
        with self.connection:
            existing = self.connection.execute(
                """
                SELECT r.id AS request_id, r.request_code, r.customer_phone, r.items_json,
                       r.sales_order_id, so.order_code, so.status, so.total_amount
                FROM storefront_order_requests r
                JOIN sales_orders so ON so.id = r.sales_order_id
                WHERE r.client_request_id = ?
                """,
                (client_request_id,),
            ).fetchone()
            if existing is not None:
                existing_items = json.loads(existing["items_json"])
                request_signature = [
                    (item["item_code"], item["quantity"]) for item in items
                ]
                existing_signature = [
                    (item["item_code"], item["quantity"]) for item in existing_items
                ]
                def normalized_phone(value: str) -> str:
                    return "".join(
                        character for character in value if character.isdigit()
                    )

                if (
                    normalized_phone(existing["customer_phone"])
                    != normalized_phone(customer_phone)
                    or existing_signature != request_signature
                ):
                    raise ValueError(
                        "Mã gửi trùng lặp đã được dùng cho yêu cầu khác."
                    )
                return {
                    "request_id": int(existing["request_id"]),
                    "request_code": existing["request_code"],
                    "sales_order_id": int(existing["sales_order_id"]),
                    "sales_order_code": existing["order_code"],
                    "sales_order_status": existing["status"],
                    "sales_order_total": float(existing["total_amount"]),
                }

            product_lines: list[dict[str, Any]] = []
            combo_lines: list[dict[str, Any]] = []
            normalized_items: list[dict[str, Any]] = []

            def available_item_quantity(item_id: int) -> float:
                row = self.connection.execute(
                    """
                    SELECT COALESCE(SUM(CASE
                               WHEN b.expiry_date IS NULL
                                 OR b.expiry_date >= date('now', 'localtime')
                               THEN b.quantity_remaining ELSE 0 END), 0)
                           - COALESCE((
                               SELECT SUM(pi.quantity)
                               FROM sales_product_items pi
                               JOIN sales_orders so ON so.id = pi.order_id
                               WHERE pi.item_id = i.id
                                 AND so.status IN ('OPEN', 'PARTIALLY_PAID')
                                 AND so.inventory_fulfilled_at IS NULL
                           ), 0) AS available
                    FROM inventory_items i
                    LEFT JOIN inventory_batches b ON b.item_id = i.id
                    WHERE i.id = ? AND i.is_active = 1
                    GROUP BY i.id
                    """,
                    (item_id,),
                ).fetchone()
                return float(row["available"] or 0) if row else 0.0

            for item in items:
                item_code = item["item_code"]
                quantity = item["quantity"]
                product = self.connection.execute(
                    """
                    SELECT id, name, is_demo, retail_price
                    FROM inventory_items
                    WHERE item_code = ? AND is_active = 1
                    """,
                    (item_code,),
                ).fetchone()
                if product is not None:
                    if product["is_demo"] or float(product["retail_price"] or 0) <= 0:
                        raise ValueError(
                            f"{product['name']} chưa được xác minh hoặc chưa có giá; "
                            "không thể tạo đơn bán tự động."
                        )
                    if available_item_quantity(int(product["id"])) < 5:
                        raise ValueError(
                            f"{product['name']} còn dưới 5 sản phẩm khả dụng; "
                            "đã được chuyển sang hết hàng."
                        )
                    product_lines.append(
                        {"item_id": product["id"], "quantity": quantity}
                    )
                    normalized_items.append(
                        {
                            "item_code": item_code,
                            "name": product["name"],
                            "quantity": quantity,
                        }
                    )
                    continue

                combo = self.connection.execute(
                    """
                    SELECT id, name, is_demo, sale_price
                    FROM product_combos
                    WHERE combo_code = ? AND is_active = 1
                    """,
                    (item_code,),
                ).fetchone()
                if combo is None:
                    raise ValueError(f"Sản phẩm {item_code} không còn trong catalog.")
                if combo["is_demo"] or float(combo["sale_price"] or 0) <= 0:
                    raise ValueError(
                        f"{combo['name']} chưa được xác minh hoặc chưa có giá; "
                        "không thể tạo đơn bán tự động."
                    )
                components = self.connection.execute(
                    """
                    SELECT ci.item_id, ci.quantity
                    FROM product_combo_items ci
                    JOIN inventory_items i ON i.id = ci.item_id AND i.is_active = 1
                    WHERE ci.combo_id = ?
                    """,
                    (combo["id"],),
                ).fetchall()
                if not components:
                    raise ValueError(f"{combo['name']} chưa có thành phần khả dụng.")
                combo_available = min(
                    (
                        available_item_quantity(int(component["item_id"]))
                        / float(component["quantity"])
                        for component in components
                        if float(component["quantity"]) > 0
                    ),
                    default=0,
                )
                if len(components) != self.connection.execute(
                    "SELECT COUNT(*) FROM product_combo_items WHERE combo_id = ?",
                    (combo["id"],),
                ).fetchone()[0] or combo_available < 5:
                    raise ValueError(
                        f"{combo['name']} còn dưới 5 combo khả dụng; "
                        "đã được chuyển sang hết hàng."
                    )
                combo_lines.append({"combo_id": combo["id"], "quantity": quantity})
                normalized_items.append(
                    {
                        "item_code": item_code,
                        "name": combo["name"],
                        "quantity": quantity,
                    }
                )

            digits_only_phone = "".join(
                character for character in customer_phone if character.isdigit()
            )
            customer = next(
                (
                    row
                    for row in self.connection.execute(
                        "SELECT id, phone FROM customers WHERE phone <> '' ORDER BY id"
                    ).fetchall()
                    if "".join(
                        character for character in row["phone"] if character.isdigit()
                    ) == digits_only_phone
                ),
                None,
            )
            if customer is None:
                customer_id = self.customers.save_customer(
                    {
                        "customer_code": f"WEB-{secrets.token_hex(5).upper()}",
                        "name": customer_name,
                        "phone": customer_phone,
                        "address": values.get("address", ""),
                        "note": f"Tạo từ cửa hàng trực tuyến; yêu cầu {request_code}.",
                    }
                )
            else:
                customer_id = int(customer["id"])

            order_id = self.sales.create_product_order(
                {
                    "order_code": f"WEB-{request_code}",
                    "customer_id": customer_id,
                    "ordered_at": datetime.now().date().isoformat(),
                    "note": (
                        f"Đặt từ cửa hàng trực tuyến; chưa thanh toán; "
                        f"mã yêu cầu {request_code}."
                    ),
                    "product_lines": product_lines,
                    "combo_lines": combo_lines,
                }
            )
            self.sales.fulfill_unpaid_product_order(order_id)
            self._deactivate_storefront_items_below_threshold(order_id)

            request_cursor = self.connection.execute(
                """
                INSERT INTO storefront_order_requests
                    (request_code, customer_name, customer_phone, address, note,
                     items_json, sales_order_id, client_request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_code,
                    customer_name,
                    customer_phone,
                    values.get("address", ""),
                    values.get("note", ""),
                    json.dumps(normalized_items, ensure_ascii=False),
                    order_id,
                    client_request_id,
                ),
            )
            self.audit.record(
                None,
                "STOREFRONT_AUTO_ORDER",
                "sales_order",
                order_id,
                f"request_code={request_code}; customer_id={customer_id}",
            )
            self.audit.record(
                None,
                "STOREFRONT_ORDER_REQUEST",
                "storefront_order_request",
                int(request_cursor.lastrowid),
                f"request_code={request_code}; sales_order_id={order_id}",
            )
            order = self.connection.execute(
                "SELECT order_code, status, total_amount FROM sales_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            return {
                "request_id": int(request_cursor.lastrowid),
                "request_code": request_code,
                "sales_order_id": order_id,
                "sales_order_code": order["order_code"],
                "sales_order_status": order["status"],
                "sales_order_total": float(order["total_amount"]),
            }

    def _deactivate_storefront_items_below_threshold(self, order_id: int) -> None:
        item_ids = [
            row["item_id"]
            for row in self.connection.execute(
                """
                SELECT DISTINCT item_id FROM sales_product_items
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchall()
        ]
        for item_id in item_ids:
            remaining = self.connection.execute(
                """
                SELECT COALESCE(SUM(CASE
                           WHEN b.expiry_date IS NULL
                             OR b.expiry_date >= date('now', 'localtime')
                           THEN b.quantity_remaining ELSE 0 END), 0)
                       - COALESCE((
                           SELECT SUM(pi.quantity)
                           FROM sales_product_items pi
                           JOIN sales_orders so ON so.id = pi.order_id
                           WHERE pi.item_id = i.id
                             AND so.status IN ('OPEN', 'PARTIALLY_PAID')
                             AND so.inventory_fulfilled_at IS NULL
                       ), 0) AS available
                FROM inventory_items i
                LEFT JOIN inventory_batches b ON b.item_id = i.id
                WHERE i.id = ?
                GROUP BY i.id
                """,
                (item_id,),
            ).fetchone()["available"]
            if float(remaining or 0) < 5:
                self.connection.execute(
                    """
                    UPDATE inventory_items
                    SET is_active = 0, storefront_auto_inactive = 1
                    WHERE id = ? AND is_active = 1
                    """,
                    (item_id,),
                )

        combo_ids = {
            row["combo_id"]
            for row in self.connection.execute(
                """
                SELECT DISTINCT combo_id FROM sales_product_items
                WHERE order_id = ? AND combo_id IS NOT NULL
                """,
                (order_id,),
            ).fetchall()
        }
        for combo_id in combo_ids:
            components = self.connection.execute(
                """
                SELECT ci.quantity,
                       COALESCE(SUM(CASE
                           WHEN b.expiry_date IS NULL
                             OR b.expiry_date >= date('now', 'localtime')
                           THEN b.quantity_remaining ELSE 0 END), 0)
                       - COALESCE((
                           SELECT SUM(pi.quantity)
                           FROM sales_product_items pi
                           JOIN sales_orders so ON so.id = pi.order_id
                           WHERE pi.item_id = i.id
                             AND so.status IN ('OPEN', 'PARTIALLY_PAID')
                             AND so.inventory_fulfilled_at IS NULL
                       ), 0) AS available
                FROM product_combo_items ci
                JOIN inventory_items i ON i.id = ci.item_id
                LEFT JOIN inventory_batches b ON b.item_id = i.id
                WHERE ci.combo_id = ?
                GROUP BY ci.item_id
                """,
                (combo_id,),
            ).fetchall()
            combo_available = min(
                (
                    float(component["available"]) / float(component["quantity"])
                    for component in components
                    if float(component["quantity"]) > 0
                ),
                default=0,
            )
            if combo_available < 5:
                self.connection.execute(
                    """
                    UPDATE product_combos
                    SET is_active = 0, storefront_auto_inactive = 1
                    WHERE id = ? AND is_active = 1
                    """,
                    (combo_id,),
                )

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

    SALES_APPROVAL_LIMIT = 15_000_000
    SALES_APPROVAL_ACTIONS = frozenset(
        {
            "save_customer",
            "create_reservation",
            "release_reservation",
            "refund_reservation_deposit",
            "create_sales_order",
            "create_product_sales_order",
            "add_payment",
            "cancel_sales_order",
        }
    )

    def submit_sales_action(
        self, action_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if action_type not in self.SALES_APPROVAL_ACTIONS:
            raise ValueError("Thao tác bán hàng không hợp lệ.")
        if not isinstance(payload, dict):
            raise ValueError("Dữ liệu thao tác bán hàng không hợp lệ.")
        serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        if self.actor_id is None:
            raise PermissionError("Cần đăng nhập để thực hiện thao tác bán hàng.")
        self._validate_sales_action_payload(action_type, payload)

        if self.has_permission(self.actor_id, "sales.manage"):
            result = self._apply_sales_action(action_type, payload)
            return {"status": "APPLIED", "result": result}

        self._require_staff_permission("sales.request")
        amount = self._sales_action_amount(action_type, payload)
        if (
            action_type in {"cancel_sales_order", "refund_reservation_deposit"}
            and amount <= self.SALES_APPROVAL_LIMIT
        ):
            result = self._apply_sales_action(action_type, payload)
            return {"status": "APPLIED", "result": result}

        request_code = f"APR-{datetime.now(timezone.utc):%Y%m%d}-{secrets.token_hex(4).upper()}"
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO sales_approval_requests
                    (request_code, requester_id, action_type, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (request_code, self.actor_id, action_type, serialized),
            )
            request_id = int(cursor.lastrowid)
            self._audit(
                "REQUEST_SALES_APPROVAL",
                "sales_approval_request",
                request_id,
                f"request_code={request_code}; action={action_type}",
            )
        return {
            "status": "PENDING",
            "request_id": request_id,
            "request_code": request_code,
        }

    def _validate_sales_action_payload(
        self, action_type: str, payload: dict[str, Any]
    ) -> None:
        def positive_id(value: Any, label: str) -> int:
            try:
                result = int(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"{label} không hợp lệ.") from error
            if result <= 0:
                raise ValueError(f"{label} không hợp lệ.")
            return result

        if action_type == "save_customer":
            values = payload.get("values")
            if not isinstance(values, dict):
                raise ValueError("Thông tin khách hàng không hợp lệ.")
            if not str(values.get("customer_code", "")).strip() or not str(
                values.get("name", "")
            ).strip():
                raise ValueError("Mã khách hàng và họ tên là bắt buộc.")
            if payload.get("customer_id") is not None:
                positive_id(payload["customer_id"], "Mã khách hàng")
            return

        if action_type in {
            "create_reservation",
            "refund_reservation_deposit",
            "release_reservation",
        }:
            if action_type == "create_reservation":
                values = payload.get("values")
                if not isinstance(values, dict):
                    raise ValueError("Thông tin giữ chỗ không hợp lệ.")
                positive_id(values.get("customer_id"), "Mã khách hàng")
                positive_id(values.get("animal_id"), "Mã thú cưng")
                deposit = float(values.get("deposit", 0))
                if not math.isfinite(deposit) or deposit < 0:
                    raise ValueError("Tiền đặt cọc không hợp lệ.")
                return
            reservation_id = positive_id(
                payload.get("reservation_id"), "Mã lượt giữ chỗ"
            )
            reservation = self.connection.execute(
                "SELECT status FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if reservation is None or reservation["status"] != "ACTIVE":
                raise ValueError("Lượt giữ chỗ không còn hoạt động.")
            if action_type == "refund_reservation_deposit":
                values = payload.get("values")
                if not isinstance(values, dict):
                    raise ValueError("Thông tin hoàn cọc không hợp lệ.")
                amount = float(values.get("amount", 0))
                if not math.isfinite(amount) or amount <= 0:
                    raise ValueError("Số tiền hoàn cọc phải lớn hơn 0.")
                if amount > self.get_reservation_balance(reservation_id):
                    raise ValueError("Số tiền vượt quá cọc chưa hoàn.")
            return

        if action_type in {"create_sales_order", "create_product_sales_order"}:
            values = payload.get("values")
            if not isinstance(values, dict):
                raise ValueError("Thông tin đơn hàng không hợp lệ.")
            if not str(values.get("order_code", "")).strip():
                raise ValueError("Mã đơn hàng là bắt buộc.")
            positive_id(values.get("customer_id"), "Mã khách hàng")
            if action_type == "create_sales_order":
                if not isinstance(values.get("animal_ids"), list) or not values[
                    "animal_ids"
                ]:
                    raise ValueError("Đơn hàng phải có ít nhất một thú cưng.")
            elif not any(
                values.get(key)
                for key in ("product_lines", "combo_lines")
            ):
                raise ValueError("Đơn hàng phải có sản phẩm hoặc combo.")
            return

        if action_type == "add_payment":
            positive_id(payload.get("order_id"), "Mã đơn hàng")
            values = payload.get("values")
            if not isinstance(values, dict):
                raise ValueError("Thông tin thanh toán không hợp lệ.")
            amount = float(values.get("amount", 0))
            if not math.isfinite(amount) or amount <= 0:
                raise ValueError("Số tiền thanh toán phải lớn hơn 0.")
            if not isinstance(values.get("method"), str):
                raise ValueError("Phương thức thanh toán không hợp lệ.")
            return

        if action_type == "cancel_sales_order":
            self._sales_action_amount(action_type, payload)

    def _sales_action_amount(
        self, action_type: str, payload: dict[str, Any]
    ) -> float:
        if action_type == "refund_reservation_deposit":
            try:
                amount = float(payload["values"]["amount"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError("Số tiền hoàn cọc không hợp lệ.") from error
            if not math.isfinite(amount) or amount <= 0:
                raise ValueError("Số tiền hoàn cọc phải lớn hơn 0.")
            return amount
        if action_type == "cancel_sales_order":
            try:
                order_id = int(payload["order_id"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError("Đơn hàng không hợp lệ.") from error
            order = self.connection.execute(
                "SELECT total_amount, status FROM sales_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            if order is None:
                raise ValueError("Không tìm thấy đơn hàng.")
            if order["status"] != "OPEN":
                raise ValueError("Chỉ đơn chưa thanh toán mới được hủy.")
            return float(order["total_amount"])
        return 0.0

    def _apply_sales_action(
        self, action_type: str, payload: dict[str, Any]
    ) -> int | None:
        if action_type == "save_customer":
            values = payload["values"]
            customer_id = payload.get("customer_id")
            result = self.customers.save_customer(values, customer_id)
            self._audit(
                "UPDATE" if customer_id is not None else "CREATE",
                "customer",
                result,
            )
            return result
        if action_type == "create_reservation":
            values = payload["values"]
            result = self.sales.create_reservation(values)
            self._audit(
                "RESERVE",
                "animal",
                values["animal_id"],
                f"reservation_id={result}; customer_id={values['customer_id']}",
            )
            return result
        if action_type == "release_reservation":
            reservation_id = int(payload["reservation_id"])
            self.sales.release_reservation(reservation_id)
            self._audit("RELEASE_RESERVATION", "reservation", reservation_id)
            return None
        if action_type == "refund_reservation_deposit":
            reservation_id = int(payload["reservation_id"])
            values = payload["values"]
            result = self.sales.refund_reservation_deposit(reservation_id, values)
            self._audit(
                "REFUND_DEPOSIT",
                "reservation",
                reservation_id,
                f"amount={values['amount']}; method={values['method']}",
            )
            return result
        if action_type == "create_sales_order":
            values = payload["values"]
            result = self.sales.create_order(values)
            self._audit(
                "CREATE_ORDER",
                "sales_order",
                result,
                f"customer_id={values['customer_id']}; animals={values['animal_ids']}",
            )
            return result
        if action_type == "create_product_sales_order":
            values = payload["values"]
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
        if action_type == "add_payment":
            order_id = int(payload["order_id"])
            values = payload["values"]
            result = self.sales.add_payment(order_id, values)
            self._audit(
                "PAYMENT",
                "sales_order",
                order_id,
                f"amount={values['amount']}; method={values['method']}",
            )
            return result
        if action_type == "cancel_sales_order":
            order_id = int(payload["order_id"])
            item_ids = [
                row["item_id"]
                for row in self.connection.execute(
                    "SELECT DISTINCT item_id FROM sales_product_items WHERE order_id = ?",
                    (order_id,),
                ).fetchall()
            ]
            self.sales.cancel_unpaid_order(order_id)
            self.inventory.reactivate_storefront_stock(item_ids)
            self._audit("CANCEL_ORDER", "sales_order", order_id)
            return None
        raise ValueError("Thao tác bán hàng không hợp lệ.")

    def list_sales_approval_requests(self) -> list[sqlite3.Row]:
        self._require_permission("sales.view")
        approver = bool(
            self.actor_id is not None
            and self.has_permission(self.actor_id, "sales.approve")
        )
        requester_filter = "" if approver else "AND r.requester_id = ?"
        parameters: tuple[Any, ...] = () if approver else (self.actor_id,)
        return self.connection.execute(
            f"""
            SELECT r.id, r.request_code, r.requester_id, u.display_name AS requester,
                   r.action_type, r.payload_json, r.status, r.requested_at,
                   r.reviewed_by, reviewer.display_name AS reviewer,
                   r.reviewed_at, r.decision_note
            FROM sales_approval_requests r
            JOIN users u ON u.id = r.requester_id
            LEFT JOIN users reviewer ON reviewer.id = r.reviewed_by
            WHERE 1 = 1 {requester_filter}
            ORDER BY CASE WHEN r.status = 'PENDING' THEN 0 ELSE 1 END,
                     r.requested_at DESC, r.id DESC
            """,
            parameters,
        ).fetchall()

    def review_sales_approval_request(
        self, request_id: int, approve: bool, note: str = ""
    ) -> int | None:
        self._require_staff_permission("sales.approve")
        if self.actor_id is None:
            raise PermissionError("Cần đăng nhập để duyệt yêu cầu.")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            request = self.connection.execute(
                """
                SELECT requester_id, action_type, payload_json, status
                FROM sales_approval_requests WHERE id = ?
                """,
                (request_id,),
            ).fetchone()
            if request is None:
                raise ValueError("Không tìm thấy yêu cầu duyệt.")
            if request["status"] != "PENDING":
                raise ValueError("Yêu cầu này đã được xử lý.")
            if int(request["requester_id"]) == self.actor_id:
                raise ValueError("Không thể tự duyệt yêu cầu do chính mình tạo.")
            if approve:
                payload = json.loads(request["payload_json"])
                result = self._apply_sales_action(request["action_type"], payload)
                status = "APPROVED"
            else:
                result = None
                status = "REJECTED"
            self.connection.execute(
                """
                UPDATE sales_approval_requests
                SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP,
                    decision_note = ?, result_json = ?
                WHERE id = ? AND status = 'PENDING'
                """,
                (
                    status,
                    self.actor_id,
                    note.strip()[:500],
                    json.dumps({"result": result}, ensure_ascii=False),
                    request_id,
                ),
            )
            self._audit(
                "APPROVE_SALES_REQUEST" if approve else "REJECT_SALES_REQUEST",
                "sales_approval_request",
                request_id,
                f"action={request['action_type']}",
            )
            self.connection.commit()
            return result
        except BaseException:
            self.connection.rollback()
            raise

    def cancel_sales_order(self, order_id: int) -> None:
        self._require_permission("sales.manage")
        item_ids = [
            row["item_id"]
            for row in self.connection.execute(
                "SELECT DISTINCT item_id FROM sales_product_items WHERE order_id = ?",
                (order_id,),
            ).fetchall()
        ]
        self.sales.cancel_unpaid_order(order_id)
        self.inventory.reactivate_storefront_stock(item_ids)
        self._audit("CANCEL_ORDER", "sales_order", order_id)

    def list_order_payments(self, order_id: int) -> list[sqlite3.Row]:
        return self.sales.list_payments(order_id)

    def create_store_slip(
        self,
        slip_type: str,
        payload: dict[str, Any],
        created_by: int,
        linked_order_id: int | None = None,
    ) -> int:
        slip_code = (
            f"PX-{datetime.now().strftime('%Y%m%d')}-"
            f"{secrets.token_hex(3).upper()}"
        )
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO store_slips
                    (slip_code, slip_type, linked_order_id, payload_json, created_by)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    slip_code,
                    slip_type,
                    linked_order_id,
                    json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                    created_by,
                ),
            )
            self._audit(
                "CREATE_STORE_SLIP",
                "store_slip",
                int(cursor.lastrowid),
                f"type={slip_type}; code={slip_code}",
            )
        return int(cursor.lastrowid)

    def get_store_slip(self, slip_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT id, slip_code, slip_type, linked_order_id, payload_json,
                   created_by, created_at
            FROM store_slips WHERE id = ?
            """,
            (slip_id,),
        ).fetchone()

    def list_store_slips(
        self, slip_type: str, limit: int = 50
    ) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT id, slip_code, slip_type, linked_order_id, created_by, created_at
            FROM store_slips
            WHERE slip_type = ?
            ORDER BY id DESC LIMIT ?
            """,
            (slip_type, limit),
        ).fetchall()

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

    def forecast_inventory_demand(
        self, item_id: int, window_days: int = 30, horizon_days: int = 30
    ) -> dict[str, Any]:
        self._require_permission("inventory.view")
        return self.inventory.demand_forecast(item_id, window_days, horizon_days)

    def inventory_replenishment_suggestions(
        self,
        lead_time_days: int = 7,
        safety_days: int = 7,
        window_days: int = 30,
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.inventory.replenishment_suggestions(
            lead_time_days, safety_days, window_days
        )

    def inventory_stock_valuation(self) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.inventory.stock_valuation()

    def inventory_ledger_discrepancies(
        self, item_id: int | None = None
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.inventory.ledger_discrepancies(item_id)

    def inventory_expiry_overview(self) -> dict[str, Any]:
        self._require_permission("inventory.view")
        return self.inventory.expiry_overview()

    def inventory_category_overview(self) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.inventory.category_overview()

    def trace_inventory_batch(self, batch_code: str) -> dict[str, Any]:
        self._require_permission("inventory.view")
        return self.inventory.batch_trace(batch_code)

    def inventory_animal_consumption(
        self, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        return self.inventory.animal_consumption_report(start_date, end_date)

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

    def list_nutrition_foods_for_species(
        self, species: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        self._require_permission("inventory.view")
        from app.modules.nutrition.repository import FoodNutritionRepository

        return FoodNutritionRepository(self.connection).list_foods_for_species(
            species, limit
        )

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

    def seed_default_role_accounts(self) -> tuple[list[str], list[str]]:
        return self.auth.seed_default_role_accounts()

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

    def set_sales_approver(
        self, user_id: int, enabled: bool, actor_id: int | None = None
    ) -> None:
        self._require_permission("users.manage")
        acting_user_id = actor_id if actor_id is not None else self.actor_id
        self.auth.set_sales_approver(user_id, enabled)
        self.audit.record(
            acting_user_id,
            "ENABLE_SALES_APPROVER" if enabled else "DISABLE_SALES_APPROVER",
            "user",
            user_id,
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

    def list_web_dataset_records(
        self, module_id: str, include_archived: bool = False
    ) -> list[sqlite3.Row]:
        where = "module_id = ?"
        parameters: tuple[Any, ...] = (module_id,)
        if not include_archived:
            where += " AND is_archived = 0"
        return self.connection.execute(
            f"""
            SELECT id, source_key, record_json, is_archived, created_at, updated_at
            FROM web_dataset_records
            WHERE {where}
            ORDER BY id
            """,
            parameters,
        ).fetchall()

    def create_web_dataset_record(
        self, module_id: str, source_key: str, record: dict[str, Any], actor_id: int
    ) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO web_dataset_records
                    (module_id, source_key, record_json, created_by)
                VALUES (?, ?, ?, ?)
                """,
                (module_id, source_key, json.dumps(record, ensure_ascii=False), actor_id),
            )
        return int(cursor.lastrowid)

    def update_web_dataset_record(
        self,
        module_id: str,
        record_id: int,
        record: dict[str, Any],
    ) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE web_dataset_records
                SET record_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE module_id = ? AND id = ? AND is_archived = 0
                """,
                (json.dumps(record, ensure_ascii=False), module_id, record_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Bản ghi không tồn tại hoặc đã được lưu trữ.")

    def archive_web_dataset_record(
        self, module_id: str, record_id: int, actor_id: int
    ) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE web_dataset_records
                SET is_archived = 1, archived_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE module_id = ? AND id = ? AND is_archived = 0
                """,
                (actor_id, module_id, record_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Bản ghi không tồn tại hoặc đã được lưu trữ.")

    def import_web_dataset_records(
        self,
        module_id: str,
        records: list[dict[str, Any]],
        actor_id: int,
    ) -> tuple[int, int]:
        inserted = 0
        skipped = 0
        with self.connection:
            for index, record in enumerate(records):
                source_key = str(index)
                cursor = self.connection.execute(
                    """
                    INSERT OR IGNORE INTO web_dataset_records
                        (module_id, source_key, record_json, created_by)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        module_id,
                        source_key,
                        json.dumps(record, ensure_ascii=False),
                        actor_id,
                    ),
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1
        return inserted, skipped

    def list_customer_portal_accounts(
        self, status: str = "PENDING"
    ) -> list[sqlite3.Row]:
        self._require_staff_permission("sales.manage")
        if status not in {"PENDING", "ACTIVE", "REJECTED", "ALL"}:
            raise ValueError("status must be PENDING, ACTIVE, REJECTED, or ALL.")
        where = "" if status == "ALL" else "WHERE a.status = ?"
        parameters: tuple[Any, ...] = () if status == "ALL" else (status,)
        return self.connection.execute(
            f"""
            SELECT a.id, a.username, a.display_name, a.status, a.customer_id,
                   a.created_at, a.approved_at, a.reviewed_at,
                   c.customer_code, c.name AS customer_name
            FROM customer_portal_accounts a
            LEFT JOIN customers c ON c.id = a.customer_id
            {where}
            ORDER BY a.created_at DESC, a.id DESC
            """,
            parameters,
        ).fetchall()

    def approve_customer_portal_account(
        self, account_id: int, customer_id: int
    ) -> bool:
        self._require_staff_permission("sales.manage")
        if self.get_customer(customer_id) is None:
            raise ValueError("An existing customer record is required.")
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE customer_portal_accounts
                SET customer_id = ?, status = 'ACTIVE',
                    approved_at = CURRENT_TIMESTAMP, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'PENDING' AND customer_id IS NULL
                """,
                (customer_id, account_id),
            )
            if cursor.rowcount:
                self._audit(
                    "CUSTOMER_PORTAL_APPROVE",
                    "customer_portal_account",
                    account_id,
                    f"customer_id={customer_id}",
                )
        return cursor.rowcount == 1

    def reject_customer_portal_account(self, account_id: int) -> bool:
        self._require_staff_permission("sales.manage")
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE customer_portal_accounts
                SET status = 'REJECTED', reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'PENDING' AND customer_id IS NULL
                """,
                (account_id,),
            )
            if cursor.rowcount:
                self._audit(
                    "CUSTOMER_PORTAL_REJECT",
                    "customer_portal_account",
                    account_id,
                )
        return cursor.rowcount == 1

    def create_customer_portal_invite(
        self, customer_id: int, expires_in_hours: int = 24
    ) -> dict[str, Any]:
        self._require_staff_permission("sales.manage")
        if self.get_customer(customer_id) is None:
            raise ValueError("An existing customer record is required.")
        linked_account = self.connection.execute(
            """
            SELECT 1 FROM customer_portal_accounts
            WHERE customer_id = ? AND status = 'ACTIVE'
            """,
            (customer_id,),
        ).fetchone()
        if linked_account is not None:
            raise ValueError("Customer already has an active portal account.")
        if not 1 <= expires_in_hours <= 168:
            raise ValueError("Invitation expiry must be between 1 and 168 hours.")
        invite_code = secrets.token_urlsafe(32)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        ).strftime("%Y-%m-%d %H:%M:%S")
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO customer_portal_invites
                    (customer_id, token_hash, created_by, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    customer_id,
                    hashlib.sha256(invite_code.encode("utf-8")).hexdigest(),
                    self.actor_id,
                    expires_at,
                ),
            )
            invite_id = int(cursor.lastrowid)
            self._audit(
                "CUSTOMER_PORTAL_INVITE",
                "customer",
                customer_id,
                f"invite_id={invite_id}",
            )
        return {
            "id": invite_id,
            "invite_code": invite_code,
            "customer_id": customer_id,
            "expires_at": expires_at,
        }

    def list_customer_portal_invites(
        self, status: str = "ALL"
    ) -> list[sqlite3.Row]:
        self._require_staff_permission("sales.manage")
        if status not in {"ACTIVE", "EXPIRED", "REDEEMED", "ALL"}:
            raise ValueError("status must be ACTIVE, EXPIRED, REDEEMED, or ALL.")
        state_sql = """
            CASE
                WHEN i.redeemed_at IS NOT NULL THEN 'REDEEMED'
                WHEN i.expires_at <= CURRENT_TIMESTAMP THEN 'EXPIRED'
                ELSE 'ACTIVE'
            END
        """
        where = "" if status == "ALL" else f"WHERE {state_sql} = ?"
        parameters: tuple[Any, ...] = () if status == "ALL" else (status,)
        return self.connection.execute(
            f"""
            SELECT i.id, i.customer_id, c.customer_code, c.name AS customer_name,
                   i.created_by, i.created_at, i.expires_at, i.redeemed_at,
                   {state_sql} AS status
            FROM customer_portal_invites i
            JOIN customers c ON c.id = i.customer_id
            {where}
            ORDER BY i.created_at DESC, i.id DESC
            """,
            parameters,
        ).fetchall()

    def expire_customer_portal_invite(self, invite_id: int) -> bool:
        self._require_staff_permission("sales.manage")
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE customer_portal_invites
                SET expires_at = CURRENT_TIMESTAMP
                WHERE id = ? AND redeemed_at IS NULL
                  AND expires_at > CURRENT_TIMESTAMP
                """,
                (invite_id,),
            )
            if cursor.rowcount:
                self._audit(
                    "CUSTOMER_PORTAL_INVITE_EXPIRE",
                    "customer_portal_invite",
                    invite_id,
                )
        return cursor.rowcount == 1

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

    def _require_staff_permission(self, permission: str) -> None:
        if self.actor_id is None or not self.auth.has_permission(
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
