import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "HTML" / "data"


def test_product_spec_schema_has_70_unique_fields():
    schema = json.loads(
        (DATA_DIR / "product_spec_fields.json").read_text(encoding="utf-8")
    )
    fields = [
        field
        for group in schema["groups"]
        for field in group["fields"]
    ]
    field_ids = [field["id"] for field in fields]

    assert len(fields) == 70
    assert len(set(field_ids)) == 70


def test_product_catalog_contains_only_partial_official_source_references():
    catalog = json.loads(
        (DATA_DIR / "pet_product_specs.json").read_text(encoding="utf-8")
    )
    products = catalog["products"]
    schema = json.loads(
        (DATA_DIR / "product_spec_fields.json").read_text(encoding="utf-8")
    )
    field_ids = {
        field["id"]
        for group in schema["groups"]
        for field in group["fields"]
    }

    assert catalog["market"] == "VN"
    assert catalog["sourcePolicy"] == "official_sources_only"
    assert len(products) == 4
    assert len({product["id"] for product in products}) == len(products)
    for product in products:
        assert product["verificationStatus"] == "source_verified_partial"
        assert product["sources"]
        assert all(
            source["type"] == "manufacturer_product_page"
            and source["url"].startswith("https://www.royalcanin.com/vn/")
            for source in product["sources"]
        )
        assert set(product["specs"]).issubset(field_ids)


def test_generated_nutrition_pages_disclose_demo_data_and_link_verified_catalog():
    page_paths = [
        PROJECT_ROOT / "HTML" / "TRrang chính" / "nutrition_products.html",
        PROJECT_ROOT / "HTML" / "TRrang chính" / "nutrition_products_dog.html",
        PROJECT_ROOT / "HTML" / "TRrang chính" / "nutrition_products_cat.html",
    ]
    for page_path in page_paths:
        page = page_path.read_text(encoding="utf-8")
        assert "không phải danh sách hàng thật" in page
        assert "Dữ liệu mẫu tự động" in page
        assert "70 trường minh họa" in page
        assert "../Trang thông số của các sản phẩm/index.html" in page
        assert "8000 sản phẩm" not in page
        assert "hiển thị đầy đủ 70 chỉ số dinh dưỡng" not in page


def test_global_brand_directory_preserves_user_supplied_names_as_unverified():
    catalog = json.loads(
        (DATA_DIR / "pet_food_brands_global.json").read_text(encoding="utf-8")
    )
    brand_names = {
        entry["name"]
        for section in catalog["sections"]
        for entry in section["entries"]
    }
    assert catalog["sourcePolicy"] == "user_supplied_unverified"
    assert "have not been independently verified" in catalog["notice"]
    assert len(catalog["sections"]) == 14
    assert {"Purina", "Royal Canin", "Orijen", "Acana", "SmartHeart", "The Best"} <= brand_names
    for section in catalog["sections"]:
        assert section["type"] in {"country", "market"}
        assert all(isinstance(entry.get("lines", []), list) for entry in section["entries"])

    page = (
        PROJECT_ROOT
        / "HTML"
        / "Trang thông số của các sản phẩm"
        / "thuong-hieu.html"
    ).read_text(encoding="utf-8")
    assert "Thông tin đang chờ xác minh độc lập" in page
    assert "index.html" in page
