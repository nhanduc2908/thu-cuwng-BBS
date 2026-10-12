import csv
import sqlite3

import pytest

from scripts.apply_catalog_vat_prices import (
    AUDIT_ACTION,
    apply_prices,
    calculate_vat_price,
    read_proposal,
    validate_proposal_covers_catalog,
    write_applied_report,
)


def create_catalog(connection):
    connection.executescript(
        """
        CREATE TABLE inventory_items (
            item_code TEXT PRIMARY KEY, retail_price REAL NOT NULL,
            is_active INTEGER NOT NULL, updated_at TEXT
        );
        CREATE TABLE product_combos (
            combo_code TEXT PRIMARY KEY, sale_price REAL NOT NULL,
            is_active INTEGER NOT NULL, updated_at TEXT
        );
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id INTEGER,
            action TEXT NOT NULL, entity_type TEXT NOT NULL,
            entity_id INTEGER, details TEXT NOT NULL
        );
        INSERT INTO inventory_items VALUES ('SKU-15000', 0, 1, '');
        INSERT INTO inventory_items VALUES ('SKU-OLD', 22000, 1, '');
        INSERT INTO inventory_items VALUES ('SKU-INACTIVE', 0, 0, '');
        INSERT INTO product_combos VALUES ('COMBO-1', 45000, 1, '');
        """
    )


def row(sku, price):
    return {
        "sku": sku,
        "name": sku,
        "proposed_price_vnd": str(price),
    }


def test_vat_price_adds_ten_percent_then_rounds_up_to_thousand():
    assert calculate_vat_price(15000) == {
        "base_price_vnd": 15000,
        "vat_amount_vnd": 1500,
        "rounding_adjustment_vnd": 500,
        "price_including_vat_vnd": 17000,
    }
    assert calculate_vat_price(45000)["price_including_vat_vnd"] == 50000
    with pytest.raises(ValueError):
        calculate_vat_price(0)


def test_updates_every_active_item_and_combo_and_audits_change():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_catalog(connection)
    rows = [
        {**row("SKU-15000", 15000), **calculate_vat_price(15000)},
        {**row("SKU-OLD", 22000), **calculate_vat_price(22000)},
        {**row("COMBO-1", 45000), **calculate_vat_price(45000)},
    ]

    apply_prices(connection, rows)

    assert connection.execute(
        "SELECT retail_price FROM inventory_items WHERE item_code='SKU-15000'"
    ).fetchone()[0] == 17000
    assert connection.execute(
        "SELECT retail_price FROM inventory_items WHERE item_code='SKU-OLD'"
    ).fetchone()[0] == 25000
    assert connection.execute(
        "SELECT sale_price FROM product_combos WHERE combo_code='COMBO-1'"
    ).fetchone()[0] == 50000
    assert connection.execute(
        "SELECT retail_price FROM inventory_items WHERE item_code='SKU-INACTIVE'"
    ).fetchone()[0] == 0
    assert connection.execute("SELECT action FROM audit_logs").fetchone()[0] == AUDIT_ACTION


def test_catalog_mismatch_fails_before_any_price_is_changed():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_catalog(connection)

    with pytest.raises(ValueError, match="không khớp catalog"):
        apply_prices(connection, [{**row("SKU-15000", 15000), **calculate_vat_price(15000)}])

    assert connection.execute(
        "SELECT retail_price FROM inventory_items WHERE item_code='SKU-15000'"
    ).fetchone()[0] == 0


def test_applied_report_records_vat_and_rounding(tmp_path):
    report = tmp_path / "prices.csv"
    rows = [
        {
            **row("SKU-15000", 15000),
            **calculate_vat_price(15000),
        }
    ]

    write_applied_report(report, rows)

    with report.open(encoding="utf-8-sig", newline="") as file:
        saved = next(csv.DictReader(file))
    assert saved["vat_rate_percent"] == "10"
    assert saved["vat_amount_vnd"] == "1500"
    assert saved["rounding_adjustment_vnd"] == "500"
    assert saved["price_including_vat_vnd"] == "17000"
    assert saved["approval_status"].startswith("Đã áp dụng")


def test_proposal_reader_rejects_duplicate_sku(tmp_path):
    proposal = tmp_path / "proposal.csv"
    proposal.write_text(
        "sku,name,proposed_price_vnd\nSKU-1,One,15000\nSKU-1,Duplicate,20000\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="trùng"):
        read_proposal(proposal)
