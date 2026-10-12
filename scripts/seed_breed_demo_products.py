"""Add clearly labeled, non-sale demo food and care SKUs for the breed catalog."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import DEFAULT_DATABASE_PATH, Database

BREED_PROFILES = ROOT / "HTML" / "data" / "pet_breed_nutrition_profiles_200.json"
GROWTH_STAGES = (
    ("YOUNG", "Tăng trưởng"),
    ("ADULT", "Trưởng thành"),
    ("SENIOR", "Lớn tuổi · đánh giá cá thể"),
)
SUPPLEMENT_LABELS = tuple(
    f"Thực phẩm bổ sung mẫu {index:02d}" for index in range(1, 25)
)
CARE_LABELS = tuple(
    f"Sản phẩm chăm sóc mẫu {index:02d}" for index in range(1, 25)
)
DEMO_NOTICE = (
    "SKU demo để kiểm thử catalog, chưa phải hàng thương mại. Chưa xác minh nhãn, "
    "thành phần, nhà sản xuất, giá hoặc tồn kho; thẻ giống chỉ phục vụ tra cứu, "
    "không phải khuyến nghị phù hợp cá thể hay công dụng phòng/ngừa/điều trị. "
    "Đối chiếu nhãn và hỏi bác sĩ thú y khi thú có bệnh hoặc đang dùng thuốc."
)
FOOD_NOTICE = (
    "Mẫu dữ liệu tham khảo theo giai đoạn sống, không đại diện công thức đã được "
    "kiểm nghiệm hoặc thức ăn hoàn chỉnh/cân bằng. Chọn sản phẩm thực theo nhãn "
    "đúng loài và giai đoạn; hỏi bác sĩ thú y khi cần chế độ đặc biệt."
)
INSERT_SQL = """
    INSERT OR IGNORE INTO inventory_items (
        item_code, name, category, unit, minimum_stock, description,
        catalog_category, target_species, age_group, brand, retail_price,
        is_demo, animal_subspecies, age_unit, life_stage, food_category,
        food_type, feeding_frequency, purpose
    ) VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, 'Mẫu demo / chưa xác minh', 0,
              1, ?, 'LABEL', ?, ?, ?, ?, ?)
"""


def load_breed_profiles(path: Path = BREED_PROFILES) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 200:
        raise ValueError("Tệp hồ sơ giống phải có đúng 200 hồ sơ.")
    breeds = []
    seen = set()
    for profile in profiles:
        species = str(profile.get("species", "")).strip().upper()
        name = str(profile.get("name", "")).strip()
        code = str(profile.get("id", "")).strip().upper().replace("-", "_")
        if species not in {"DOG", "CAT"} or not name or not code:
            raise ValueError("Hồ sơ giống thiếu mã, tên hoặc loài hợp lệ.")
        if code in seen:
            raise ValueError(f"Mã giống bị trùng: {code}")
        seen.add(code)
        breeds.append({"species": species, "name": name, "code": code})
    return breeds


def build_demo_products(
    breeds: list[dict[str, str]],
) -> list[tuple[object, ...]]:
    if len(breeds) != 200:
        raise ValueError("Chỉ tạo catalog khi có đủ 200 hồ sơ giống.")

    rows: list[tuple[object, ...]] = []
    for index, breed in enumerate(breeds):
        species, name, code = breed["species"], breed["name"], breed["code"]
        species_label = "chó" if species == "DOG" else "mèo"
        for stage, stage_label in GROWTH_STAGES:
            rows.append(
                (
                    f"DEMO-BREED-{code}-FOOD-{stage}",
                    f"Mẫu thức ăn {species_label} · {name} · {stage_label}",
                    "FOOD",
                    "mẫu demo",
                    FOOD_NOTICE,
                    "Thức ăn mẫu theo giai đoạn",
                    species,
                    stage_label,
                    name,
                    stage,
                    "Mẫu tham khảo",
                    "Theo nhãn",
                    "Theo nhãn sau xác minh",
                    FOOD_NOTICE,
                )
            )

        supplement_count = 24 if index % 2 == 0 else 23
        for item_index in range(supplement_count):
            rows.append(
                (
                    f"DEMO-BREED-{code}-SUP-{item_index + 1:02d}",
                    f"{SUPPLEMENT_LABELS[item_index]} · {name}",
                    "FOOD",
                    "mẫu demo",
                    DEMO_NOTICE,
                    "Thực phẩm bổ sung mẫu",
                    species,
                    "Theo nhãn",
                    name,
                    "",
                    "Thức ăn bổ sung mẫu",
                    "Theo nhãn",
                    "Theo nhãn sau xác minh",
                    DEMO_NOTICE,
                )
            )

        care_count = 47 - supplement_count
        for item_index in range(care_count):
            rows.append(
                (
                    f"DEMO-BREED-{code}-CARE-{item_index + 1:02d}",
                    f"{CARE_LABELS[item_index]} · {name}",
                    "SUPPLIES",
                    "mẫu demo",
                    DEMO_NOTICE,
                    "Sản phẩm chăm sóc mẫu",
                    species,
                    "Theo nhãn",
                    name,
                    "",
                    "",
                    "",
                    "Theo hướng dẫn nhãn sau xác minh",
                    DEMO_NOTICE,
                )
            )
    if len(rows) != 10_000:
        raise ValueError(f"Catalog sinh ra {len(rows)} dòng thay vì 10.000.")
    return rows


def insert_demo_products(
    connection: sqlite3.Connection,
    rows: list[tuple[object, ...]],
) -> int:
    with connection:
        before = connection.total_changes
        connection.executemany(INSERT_SQL, rows)
        return connection.total_changes - before


def backup_database(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.before-breed-products-{stamp}{path.suffix}.bak")
    source = sqlite3.connect(path)
    try:
        destination = sqlite3.connect(backup)
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help="PetCare SQLite database.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up the database and insert the 10,000 demo records.",
    )
    args = parser.parse_args()
    database_path = args.database.expanduser().resolve()
    if not database_path.is_file():
        parser.error(f"PetCare database does not exist: {database_path}")
    rows = build_demo_products(load_breed_profiles())
    if not args.apply:
        print(f"Dry run: ready to add {len(rows)} demo products to the app database.")
        return 0

    backup_path = backup_database(database_path)
    database = Database(database_path)
    try:
        added = insert_demo_products(database.connection, rows)
        admin = database.connection.execute(
            "SELECT id FROM users WHERE role = 'ADMIN' AND is_active = 1 ORDER BY id LIMIT 1"
        ).fetchone()
        if admin:
            database.set_actor(int(admin["id"]))
        database.audit.record(
            database.actor_id,
            "BULK_CREATE",
            "inventory_item",
            details=f"Added {added} demo food/care SKUs for 200 breeds; no medicines or stock.",
        )
    finally:
        database.close()

    printable_backup = str(backup_path).encode("ascii", "backslashreplace").decode("ascii")
    print(f"Added {added} demo products; database backup: {printable_backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
