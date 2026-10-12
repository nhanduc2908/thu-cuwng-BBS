"""Generate factual catalog descriptions and an unapplied price proposal CSV."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import DEFAULT_DATABASE_PATH

DEFAULT_PROPOSAL_PATH = (
    ROOT / "HTML" / "Web bán hàng" / "data" / "store_price_proposal.csv"
)
PRICE_PROPOSAL_BASE = 15_000
SPECIES_LABELS = {
    "DOG": "Chó",
    "CAT": "Mèo",
    "RABBIT": "Thỏ",
    "HAMSTER": "Hamster",
    "BIRD": "Chim",
    "FISH": "Cá",
    "REPTILE": "Bò sát",
}
STAGE_LABELS = {
    "YOUNG": "Tăng trưởng",
    "ADULT": "Trưởng thành",
    "SENIOR": "Lớn tuổi",
}
FOOD_FACTS = (
    ("food_category", "Nhóm thức ăn"),
    ("food_type", "Dạng thức ăn"),
    ("food_subtype", "Phân loại thức ăn"),
    ("ingredients", "Thành phần"),
    ("protein_source", "Nguồn protein"),
    ("nutrition_type", "Loại dinh dưỡng"),
    ("diet_type", "Chế độ ăn"),
    ("purpose", "Mục đích"),
    ("vitamin_c_content", "Vitamin C"),
    ("water_level", "Độ ẩm"),
    ("feeding_frequency", "Tần suất"),
    ("feeding_time", "Thời điểm"),
    ("serving_size", "Khẩu phần"),
)
CARE_FACTS = (
    ("purpose", "Mục đích ghi trong catalog"),
    ("ingredients", "Thành phần ghi trong catalog"),
)
DESCRIPTION_NOTE = (
    "Mô tả được tổng hợp từ các trường đang có trong catalog, không bổ sung "
    "thành phần, tác dụng hoặc hướng dẫn ngoài dữ liệu. Đối chiếu nhãn gốc "
    "trước khi sử dụng."
)


def _value(row: sqlite3.Row | dict[str, object], key: str) -> str:
    value = row[key]
    return str(value).strip() if value is not None else ""


def _species(value: str) -> str:
    parts = [
        SPECIES_LABELS.get(part.strip().upper(), part.strip())
        for part in value.split(",")
        if part.strip()
    ]
    return ", ".join(parts) or ""


def _is_unverified_placeholder(value: str) -> bool:
    normalized = value.casefold()
    return (
        normalized in {
            "phân loại catalog; kiểm tra nhãn",
            "theo nhãn sau xác minh",
            "theo nhãn",
            "theo hướng dẫn nhãn sau xác minh",
            "mẫu tham khảo",
        }
        or "chưa xác minh" in normalized
        or "mẫu demo" in normalized
        or normalized.startswith("mẫu dữ liệu tham khảo")
    )


def build_product_description(row: sqlite3.Row | dict[str, object]) -> str:
    name = _value(row, "name") or "Sản phẩm chưa có tên"
    category = _value(row, "catalog_category") or _value(row, "category")
    facts = [name]
    if category:
        facts.append(f"Danh mục: {category}")

    species = _species(_value(row, "target_species"))
    if species:
        facts.append(f"Loài ghi trong catalog: {species}")
    breed = _value(row, "animal_subspecies")
    if breed:
        facts.append(f"Giống được gắn trong catalog: {breed}")

    age_group = _value(row, "age_group")
    life_stage = STAGE_LABELS.get(
        _value(row, "life_stage").upper(), _value(row, "life_stage")
    )
    stage_values = []
    for value in (age_group, life_stage):
        if value and value.casefold() not in {existing.casefold() for existing in stage_values}:
            stage_values.append(value)
    stage = " · ".join(stage_values)
    if stage:
        facts.append(f"Nhóm tuổi/giai đoạn ghi trong catalog: {stage}")

    for key, label in (
        ("pack_size", "Quy cách"),
        ("unit", "Đơn vị"),
        ("brand", "Thương hiệu"),
    ):
        value = _value(row, key)
        if value and "chưa xác định" not in value.casefold() and not _is_unverified_placeholder(value):
            facts.append(f"{label}: {value}")

    if _value(row, "category").upper() == "FOOD":
        source_facts = FOOD_FACTS
    else:
        source_facts = CARE_FACTS
    for key, label in source_facts:
        value = _value(row, key)
        if value and not _is_unverified_placeholder(value):
            facts.append(f"{label}: {value}")

    missing_fields = [
        ("ingredients", "thành phần"),
        ("brand", "thương hiệu đã xác minh"),
        ("pack_size", "quy cách"),
    ]
    if _value(row, "category").upper() == "FOOD":
        missing_fields.extend(
            [
                ("protein_source", "nguồn protein"),
                ("nutrition_type", "thông tin dinh dưỡng"),
                ("serving_size", "khẩu phần"),
            ]
        )
    else:
        missing_fields.append(("purpose", "mục đích sử dụng"))
    missing = []
    for key, label in missing_fields:
        value = _value(row, key)
        if not value or "chưa xác định" in value.casefold() or _is_unverified_placeholder(value):
            missing.append(label)
    if _is_unverified_placeholder(_value(row, "unit")):
        missing.append("đơn vị bán")
    if missing:
        facts.append(f"Chưa có dữ liệu catalog về: {', '.join(missing)}")
    facts.append(DESCRIPTION_NOTE)
    return ". ".join(facts)


def build_combo_description(
    row: sqlite3.Row | dict[str, object],
    component_names: list[str],
) -> str:
    name = _value(row, "name") or "Combo chưa có tên"
    facts = [name]
    species = _species(_value(row, "target_species"))
    if species:
        facts.append(f"Loài ghi trong catalog: {species}")
    facts.append(
        f"SKU thành phần đã cấu hình: {', '.join(component_names)}"
        if component_names
        else "Chưa cấu hình SKU thành phần trong catalog"
    )
    facts.append(DESCRIPTION_NOTE)
    return ". ".join(facts)


def proposal_price(current_price: object) -> tuple[int, str]:
    try:
        current = float(current_price or 0)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Giá hiện tại không hợp lệ: {current_price!r}") from error
    if current > 0:
        return round(current), "Giữ giá đang có làm mốc đề xuất; chưa được xác minh"
    return PRICE_PROPOSAL_BASE, "Mức tham khảo khoảng 15.000 VND; cần duyệt theo SKU và quy cách"


def create_database_backup(database_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = database_path.with_name(
        f"{database_path.stem}.before-catalog-enrichment-{stamp}{database_path.suffix}.bak"
    )
    with sqlite3.connect(database_path) as source, sqlite3.connect(backup_path) as backup:
        source.backup(backup)
    return backup_path


def write_price_proposal(
    connection: sqlite3.Connection,
    output_path: Path = DEFAULT_PROPOSAL_PATH,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    products = connection.execute(
        """
        SELECT item_code AS sku, name, category, catalog_category,
               target_species, animal_subspecies, age_group, life_stage,
               pack_size, retail_price AS current_price, description
        FROM inventory_items
        WHERE is_active = 1
        ORDER BY item_code
        """
    ).fetchall()
    combos = connection.execute(
        """
        SELECT c.combo_code AS sku, c.name, 'COMBO' AS category,
               'Combo' AS catalog_category, c.target_species,
               '' AS animal_subspecies, '' AS age_group, '' AS life_stage,
               '' AS pack_size, c.sale_price AS current_price, c.description
        FROM product_combos c
        WHERE c.is_active = 1
        ORDER BY c.combo_code
        """
    ).fetchall()

    headers = [
        "sku",
        "name",
        "category",
        "catalog_category",
        "target_species",
        "breed_tag",
        "age_group",
        "life_stage",
        "pack_size",
        "current_price_vnd",
        "proposed_price_vnd",
        "proposal_basis",
        "description",
        "approval_status",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in [*products, *combos]:
            price, basis = proposal_price(row["current_price"])
            writer.writerow(
                {
                    "sku": row["sku"],
                    "name": row["name"],
                    "category": row["category"],
                    "catalog_category": row["catalog_category"],
                    "target_species": row["target_species"],
                    "breed_tag": row["animal_subspecies"],
                    "age_group": row["age_group"],
                    "life_stage": row["life_stage"],
                    "pack_size": row["pack_size"],
                    "current_price_vnd": row["current_price"] or "",
                    "proposed_price_vnd": price,
                    "proposal_basis": basis,
                    "description": row["description"],
                    "approval_status": "Chưa được duyệt; không cập nhật vào giá bán",
                }
            )
    return len(products) + len(combos)


def enrich_database(connection: sqlite3.Connection) -> int:
    rows = connection.execute(
        "SELECT * FROM inventory_items WHERE is_active = 1 ORDER BY id"
    ).fetchall()
    with connection:
        connection.executemany(
            "UPDATE inventory_items SET description = ? WHERE id = ?",
            [
                (build_product_description(row), row["id"])
                for row in rows
            ],
        )
        combos = connection.execute(
            """
            SELECT c.id, c.name, c.target_species, c.description,
                   GROUP_CONCAT(i.name, ' | ') AS component_names
            FROM product_combos c
            LEFT JOIN product_combo_items ci ON ci.combo_id = c.id
            LEFT JOIN inventory_items i ON i.id = ci.item_id
            WHERE c.is_active = 1
            GROUP BY c.id
            """
        ).fetchall()
        for combo in combos:
            names = [
                name for name in _value(combo, "component_names").split(" | ") if name
            ]
            connection.execute(
                "UPDATE product_combos SET description = ? WHERE id = ?",
                (build_combo_description(combo, names), combo["id"]),
            )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--proposal-output", type=Path, default=DEFAULT_PROPOSAL_PATH)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up SQLite, refresh factual descriptions, and write price proposals only.",
    )
    args = parser.parse_args()
    database_path = args.database.expanduser().resolve()
    proposal_path = args.proposal_output.expanduser().resolve()
    if not database_path.is_file():
        parser.error(f"PetCare database does not exist: {database_path}")

    if not args.apply:
        with sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True) as connection:
            count = connection.execute(
                "SELECT count(*) FROM inventory_items WHERE is_active = 1"
            ).fetchone()[0]
            combo_count = connection.execute(
                "SELECT count(*) FROM product_combos WHERE is_active = 1"
            ).fetchone()[0]
        print(
            f"Dry run: {count} product descriptions, {combo_count} combo descriptions, "
            f"and {count + combo_count} price proposals. No database changes."
        )
        return 0

    backup_path = create_database_backup(database_path)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        item_count = enrich_database(connection)
        price_count = write_price_proposal(connection, proposal_path)
    finally:
        connection.close()
    printable_backup = str(backup_path).encode("ascii", "backslashreplace").decode("ascii")
    printable_proposal = str(proposal_path).encode("ascii", "backslashreplace").decode("ascii")
    print(
        f"Updated {item_count} product descriptions and wrote {price_count} "
        f"unapproved price proposals. Database backup: {printable_backup}. "
        f"Price proposal: {printable_proposal}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
