import csv
import sqlite3

from scripts.enrich_catalog_descriptions import (
    DESCRIPTION_NOTE,
    build_combo_description,
    build_product_description,
    enrich_database,
    proposal_price,
    write_price_proposal,
)


def test_product_descriptions_only_repeat_catalog_facts_and_mark_unknowns():
    product = {
        "name": "Hạt mèo Adult",
        "category": "FOOD",
        "catalog_category": "Thức ăn cho mèo",
        "target_species": "CAT",
        "animal_subspecies": "Maine Coon",
        "age_group": "Adult",
        "life_stage": "ADULT",
        "pack_size": "",
        "unit": "gói",
        "brand": "Mẫu demo / chưa xác minh",
        "food_category": "Thức ăn hoàn chỉnh",
        "food_type": "Hạt khô",
        "ingredients": "",
        "protein_source": "",
        "nutrition_type": "",
        "diet_type": "",
        "purpose": "Phân loại catalog; kiểm tra nhãn",
        "vitamin_c_content": "",
        "water_level": "",
        "feeding_frequency": "Theo hướng dẫn sản phẩm",
        "feeding_time": "",
        "serving_size": "",
        "food_subtype": "",
    }

    description = build_product_description(product)

    assert "Hạt mèo Adult" in description
    assert "Loài ghi trong catalog: Mèo" in description
    assert "Giống được gắn trong catalog: Maine Coon" in description
    assert "Dạng thức ăn: Hạt khô" in description
    assert "thành phần" in description
    assert "thông tin dinh dưỡng" in description
    assert "không bổ sung thành phần" in description
    assert "công thức riêng" not in description
    assert "Nhóm tuổi/giai đoạn ghi trong catalog: Adult · Trưởng thành" in description


def test_unverified_placeholder_purpose_is_not_presented_as_a_product_claim():
    product = {
        "name": "Mẫu thức ăn chó · Breed · Tăng trưởng",
        "category": "FOOD",
        "catalog_category": "Thức ăn mẫu theo giai đoạn",
        "target_species": "DOG",
        "animal_subspecies": "Breed",
        "age_group": "Tăng trưởng",
        "life_stage": "YOUNG",
        "pack_size": "",
        "unit": "mẫu demo",
        "brand": "Mẫu demo / chưa xác minh",
        "food_category": "Mẫu tham khảo",
        "food_type": "Theo nhãn",
        "ingredients": "",
        "protein_source": "",
        "nutrition_type": "",
        "diet_type": "",
        "purpose": "Mẫu dữ liệu tham khảo theo giai đoạn sống.",
        "vitamin_c_content": "",
        "water_level": "",
        "feeding_frequency": "Theo nhãn sau xác minh",
        "feeding_time": "",
        "serving_size": "",
        "food_subtype": "",
    }

    description = build_product_description(product)

    assert "Mục đích:" not in description
    assert "Nhóm thức ăn: Mẫu tham khảo" not in description
    assert "Đơn vị: mẫu demo" not in description
    assert "Nhóm tuổi/giai đoạn ghi trong catalog: Tăng trưởng" in description
    assert "đơn vị bán" in description


def test_combo_descriptions_list_configured_components_only():
    description = build_combo_description(
        {"name": "Combo chó", "target_species": "DOG,CAT"},
        ["Hạt chó", "Bát"],
    )

    assert "Loài ghi trong catalog: Chó, Mèo" in description
    assert "SKU thành phần đã cấu hình: Hạt chó, Bát" in description
    assert DESCRIPTION_NOTE in description


def test_price_proposals_retain_existing_prices_and_do_not_claim_approval(tmp_path):
    assert proposal_price(89000) == (
        89000,
        "Giữ giá đang có làm mốc đề xuất; chưa được xác minh",
    )
    assert proposal_price(0)[0] == 15000

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY, item_code TEXT, name TEXT, category TEXT,
            catalog_category TEXT, target_species TEXT, animal_subspecies TEXT,
            age_group TEXT, life_stage TEXT, pack_size TEXT, retail_price REAL,
            description TEXT, is_active INTEGER
        );
        CREATE TABLE product_combos (
            id INTEGER PRIMARY KEY, combo_code TEXT, name TEXT, target_species TEXT,
            sale_price REAL, description TEXT, is_active INTEGER
        );
        INSERT INTO inventory_items VALUES
            (1, 'SKU-1', 'Food', 'FOOD', 'Food', 'DOG', 'Beagle', 'Adult',
             'ADULT', '1 kg', 0, 'Description', 1);
        INSERT INTO product_combos VALUES
            (1, 'COMBO-1', 'Combo', 'DOG', 45000, 'Combo description', 1);
        """
    )
    output = tmp_path / "price-proposal.csv"

    assert write_price_proposal(connection, output) == 2
    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["proposed_price_vnd"] == "15000"
    assert rows[0]["approval_status"].startswith("Chưa được duyệt")
    assert rows[1]["proposed_price_vnd"] == "45000"


def test_database_enrichment_updates_descriptions_without_touching_prices():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY, item_code TEXT, name TEXT, category TEXT,
            catalog_category TEXT, target_species TEXT, animal_subspecies TEXT,
            age_group TEXT, life_stage TEXT, pack_size TEXT, unit TEXT,
            brand TEXT, food_category TEXT, food_type TEXT, food_subtype TEXT,
            ingredients TEXT, protein_source TEXT, nutrition_type TEXT,
            diet_type TEXT, purpose TEXT, vitamin_c_content TEXT, water_level TEXT,
            feeding_frequency TEXT, feeding_time TEXT, serving_size TEXT,
            description TEXT, is_active INTEGER, retail_price REAL
        );
        CREATE TABLE product_combos (
            id INTEGER PRIMARY KEY, name TEXT, target_species TEXT,
            description TEXT, is_active INTEGER
        );
        CREATE TABLE product_combo_items (
            combo_id INTEGER, item_id INTEGER
        );
        INSERT INTO inventory_items VALUES
            (1, 'SKU-1', 'Item one', 'FOOD', 'Food', 'DOG', '', 'Adult',
             'ADULT', '1 kg', 'bag', '', 'Complete', 'Dry', '', '', '', '', '',
             '', '', '', '', '', '', 'Old description', 1, 25000);
        INSERT INTO product_combos VALUES
            (1, 'Combo one', 'DOG', 'Old combo', 1);
        INSERT INTO product_combo_items VALUES (1, 1);
        """
    )

    assert enrich_database(connection) == 1
    product = connection.execute(
        "SELECT description, retail_price FROM inventory_items WHERE id = 1"
    ).fetchone()
    combo = connection.execute(
        "SELECT description FROM product_combos WHERE id = 1"
    ).fetchone()
    assert "Item one" in product["description"]
    assert product["retail_price"] == 25000
    assert "SKU thành phần đã cấu hình: Item one" in combo["description"]
