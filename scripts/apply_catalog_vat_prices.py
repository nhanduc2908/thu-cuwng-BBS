"""Apply approved proposal prices plus 10% VAT to every active product and combo."""

from __future__ import annotations

import argparse
import csv
import sys
import math
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.enrich_catalog_descriptions import (
    DEFAULT_PROPOSAL_PATH,
    create_database_backup,
)
from app.database import DEFAULT_DATABASE_PATH


VAT_RATE_PERCENT = 10
ROUNDING_INCREMENT_VND = 1_000
AUDIT_ACTION = "BULK_PRICE_UPDATE"
AUDIT_DETAILS = (
    "Applied proposal prices plus 10% VAT, rounded up to the nearest 1,000 VND, "
    "to all active inventory items and combos per user approval."
)
REPORT_FIELDS = (
    "sku",
    "name",
    "base_price_vnd",
    "vat_rate_percent",
    "vat_amount_vnd",
    "rounding_adjustment_vnd",
    "price_including_vat_vnd",
    "approval_status",
)


def calculate_vat_price(base_price: object) -> dict[str, int]:
    try:
        base = int(base_price)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Giá đề xuất không hợp lệ: {base_price!r}") from error
    if base <= 0:
        raise ValueError(f"Giá đề xuất phải lớn hơn 0: {base_price!r}")
    vat_amount = (base * VAT_RATE_PERCENT + 50) // 100
    with_vat = base + vat_amount
    rounded = (
        math.ceil(with_vat / ROUNDING_INCREMENT_VND) * ROUNDING_INCREMENT_VND
    )
    return {
        "base_price_vnd": base,
        "vat_amount_vnd": vat_amount,
        "rounding_adjustment_vnd": rounded - with_vat,
        "price_including_vat_vnd": rounded,
    }


def read_proposal(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows or not {"sku", "name", "proposed_price_vnd"} <= set(rows[0]):
        raise ValueError("Bảng giá đề xuất thiếu cột SKU, tên hoặc giá đề xuất.")
    seen: set[str] = set()
    prepared = []
    for row in rows:
        sku = row["sku"].strip()
        if not sku or sku in seen:
            raise ValueError(f"Mã SKU trống hoặc trùng trong bảng giá: {sku!r}")
        seen.add(sku)
        prepared.append({**row, **calculate_vat_price(row["proposed_price_vnd"])})
    return prepared


def validate_proposal_covers_catalog(
    connection: sqlite3.Connection,
    rows: list[dict[str, str | int]],
) -> None:
    database_skus = {
        str(row[0])
        for row in connection.execute(
            """
            SELECT item_code FROM inventory_items WHERE is_active = 1
            UNION ALL
            SELECT combo_code FROM product_combos WHERE is_active = 1
            """
        )
    }
    proposal_skus = {str(row["sku"]) for row in rows}
    if database_skus != proposal_skus:
        missing = sorted(database_skus - proposal_skus)[:10]
        extra = sorted(proposal_skus - database_skus)[:10]
        raise ValueError(
            "Bảng giá không khớp catalog đang hoạt động "
            f"(thiếu tối đa 10: {missing}; không tồn tại/tắt tối đa 10: {extra})."
        )


def apply_prices(
    connection: sqlite3.Connection,
    rows: list[dict[str, str | int]],
) -> None:
    validate_proposal_covers_catalog(connection, rows)
    with connection:
        for row in rows:
            sku = str(row["sku"])
            price = int(row["price_including_vat_vnd"])
            product_cursor = connection.execute(
                """
                UPDATE inventory_items SET retail_price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE item_code = ? AND is_active = 1
                """,
                (price, sku),
            )
            if product_cursor.rowcount == 1:
                continue
            combo_cursor = connection.execute(
                """
                UPDATE product_combos SET sale_price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE combo_code = ? AND is_active = 1
                """,
                (price, sku),
            )
            if combo_cursor.rowcount != 1:
                raise ValueError(f"Không thể cập nhật chính xác một mặt hàng cho SKU {sku}.")
        connection.execute(
            """
            INSERT INTO audit_logs
                (actor_id, action, entity_type, entity_id, details)
            VALUES (NULL, ?, 'catalog', NULL, ?)
            """,
            (AUDIT_ACTION, f"{AUDIT_DETAILS} Total SKU: {len(rows)}."),
        )


def write_applied_report(
    path: Path,
    rows: list[dict[str, str | int]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = (
        "Đã áp dụng theo yêu cầu người dùng; giá gồm 10% VAT, "
        "đã làm tròn lên 1.000đ"
    )
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sku": row["sku"],
                    "name": row.get("name", ""),
                    "base_price_vnd": row["base_price_vnd"],
                    "vat_rate_percent": VAT_RATE_PERCENT,
                    "vat_amount_vnd": row["vat_amount_vnd"],
                    "rounding_adjustment_vnd": row["rounding_adjustment_vnd"],
                    "price_including_vat_vnd": row["price_including_vat_vnd"],
                    "approval_status": status,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--proposal", type=Path, default=DEFAULT_PROPOSAL_PATH)
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_PROPOSAL_PATH.with_name("store_prices_with_vat_applied.csv"),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up SQLite and update every active inventory and combo price.",
    )
    args = parser.parse_args()
    database_path = args.database.expanduser().resolve()
    proposal_path = args.proposal.expanduser().resolve()
    report_path = args.report.expanduser().resolve()
    if not database_path.is_file():
        parser.error(f"PetCare database does not exist: {database_path}")
    if not proposal_path.is_file():
        parser.error(f"Price proposal does not exist: {proposal_path}")

    try:
        rows = read_proposal(proposal_path)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        try:
            validate_proposal_covers_catalog(connection, rows)
            if not args.apply:
                print(
                    f"Dry run: {len(rows)} active SKUs; 10% VAT; round up to "
                    f"{ROUNDING_INCREMENT_VND:,} VND. No database changes."
                )
                return 0
            backup_path = create_database_backup(database_path)
            apply_prices(connection, rows)
        finally:
            connection.close()
        write_applied_report(report_path, rows)
    except (OSError, sqlite3.Error, ValueError) as error:
        parser.error(str(error))

    printable_backup = str(backup_path).encode("ascii", "backslashreplace").decode("ascii")
    printable_report = str(report_path).encode("ascii", "backslashreplace").decode("ascii")
    print(
        f"Applied VAT-inclusive prices to {len(rows)} SKUs; SQLite backup: "
        f"{printable_backup}; report: {printable_report}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
