import csv
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "HTML" / "Web bán hàng"


class LocalLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.paths.append(value)


def test_storefront_has_eight_linked_html_pages_and_shared_assets():
    pages = sorted(STORE.glob("*.html"))
    assert len(pages) == 8
    expected_pages = {
        "index.html",
        "san-pham.html",
        "thuc-an-thu-cung.html",
        "phu-kien-thiet-bi.html",
        "chi-tiet-san-pham.html",
        "gio-hang.html",
        "thanh-toan.html",
        "dat-hang-thanh-cong.html",
    }
    assert {page.name for page in pages} == expected_pages

    for page in pages:
        parser = LocalLinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.paths:
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("#", "mailto:", "tel:")):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            assert target.is_file(), f"{page.name} has a broken local link: {reference}"


def test_store_catalog_snapshot_contains_the_full_synced_application_inventory():
    catalog = json.loads((STORE / "data" / "store_catalog.json").read_text(encoding="utf-8"))
    assert catalog["dataStatus"] == "demo_only"
    assert catalog["sourceType"] == "sqlite_snapshot"
    assert catalog["summary"]["productCount"] >= 10_000
    assert catalog["summary"]["comboCount"] >= 1
    assert catalog["summary"]["productCount"] == len(catalog["products"])
    assert catalog["summary"]["comboCount"] == len(catalog["combos"])
    assert {item["category"] for item in catalog["products"]} >= {"FOOD", "SUPPLIES"}
    assert all(item["is_demo"] for item in catalog["products"])
    assert all(item["stock_quantity"] == 0 for item in catalog["products"])
    assert all("unit_cost" not in item and "supplier_id" not in item for item in catalog["products"])
    breed_demo = [item for item in catalog["products"] if item["item_code"].startswith("DEMO-BREED-")]
    assert len(breed_demo) == 10_000
    assert all(item["description"] for item in catalog["products"])
    assert sum(item["category"] == "FOOD" and item["life_stage"] in {"YOUNG", "ADULT", "SENIOR"} for item in breed_demo) == 600
    assert sum(item["category"] == "FOOD" and item["catalog_category"] == "Thực phẩm bổ sung mẫu" for item in breed_demo) == 4_700
    assert sum(item["category"] == "SUPPLIES" for item in breed_demo) == 4_700
    proposal = STORE / "data" / "store_price_proposal.csv"
    assert proposal.is_file()
    with proposal.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == len(catalog["products"]) + len(catalog["combos"])
    assert all(row["approval_status"].startswith("Chưa được duyệt") for row in rows)
    breed_prices = [row for row in rows if row["sku"].startswith("DEMO-BREED-")]
    assert len(breed_prices) == 10_000
    assert all(row["proposed_price_vnd"] == "15000" for row in breed_prices)


def test_store_order_flow_is_local_only_and_has_required_contact_fields():
    checkout = (STORE / "thanh-toan.html").read_text(encoding="utf-8")
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    assert 'name="name"' in checkout and 'name="phone"' in checkout
    assert "local_request_only" in script
    assert "fetch(" in script
    assert "method: \"POST\"" not in script
    assert "bong-bong-store-order-v1:" in script


def test_product_details_show_only_catalog_facts_and_mark_missing_fields():
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    styles = (STORE / "styles" / "store.css").read_text(encoding="utf-8")
    assert "Chưa được cung cấp trong catalog" in script
    assert "Thành phần ghi trong catalog" in script
    assert "không thay thế nhãn sản phẩm" in script
    assert "Catalog chính thức theo xác nhận quản trị viên" in script
    assert "ownerConfirmedOfficial" in script
    assert "function formatLifeStage" in script
    assert "Giá niêm yết · đã gồm VAT 10%" in script
    assert "Giá dữ liệu demo · cần xác nhận" not in script
    assert "Dữ liệu demo · cần cửa hàng xác nhận" not in script
    assert "Không có liều dùng" not in script
    assert ".product-detail-panel" in styles
