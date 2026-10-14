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


def test_store_order_flow_submits_with_consent_and_is_not_a_local_draft():
    checkout = (STORE / "thanh-toan.html").read_text(encoding="utf-8")
    styles = (STORE / "styles" / "store.css").read_text(encoding="utf-8")
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    assert 'name="name"' in checkout and 'name="phone"' in checkout
    assert 'name="consent"' in checkout
    assert "lưu trong SQLite" in checkout
    assert "/api/storefront/order-requests" in script
    assert "local_request_only" not in script
    assert "ORDER_PREFIX" not in script
    assert "fetch(" in script
    assert 'method: "POST"' in script
    assert "/api/storefront/order-requests/${encodeURIComponent(code)}" in script
    assert ".checkout-form[hidden] { display: none; }" in styles
    assert "Đang tải bản nháp" not in (STORE / "dat-hang-thanh-cong.html").read_text(encoding="utf-8")
    assert "bản nháp lưu trên thiết bị" not in (STORE / "index.html").read_text(encoding="utf-8")
    assert "localStorage.setItem(`${ORDER_PREFIX}" not in script
    assert "salesOrderCode" in script and "salesOrderStatus" in script


def test_homepage_explains_recent_popularity_and_request_signals():
    homepage = (STORE / "index.html").read_text(encoding="utf-8")
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    assert 'data-recommendation-grid' in homepage
    assert "số lượng bán (45%)" in homepage
    assert "không tính là doanh số" in homepage
    assert "function renderRecommendations()" in script
    assert "popularity30d.score > 0" in script
    assert "Snapshot tĩnh chưa có thống kê bán hàng" in script


def test_product_catalogs_offer_consistent_sorting_and_empty_trend_explanation():
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    pages = [
        "san-pham.html",
        "thuc-an-thu-cung.html",
        "phu-kien-thiet-bi.html",
    ]
    for page_name in pages:
        page = (STORE / page_name).read_text(encoding="utf-8")
        assert 'id="catalog-sort"' in page
        assert 'value="popular">Xu hướng 30 ngày' in page
        assert 'value="price-asc">Giá thấp đến cao' in page
        assert 'value="price-desc">Giá cao đến thấp' in page
        assert 'value="stock">Còn hàng trước' in page
        assert 'data-sort-status role="status"' in page
    assert "function compareProducts(first, second, sortBy)" in script
    assert '["catalog-search", "catalog-category", "catalog-species", "catalog-sort"]' in script
    assert "danh sách xu hướng đang hiển thị theo tên" in script


def test_storefront_requires_verified_stock_and_exposes_order_status_lookup():
    checkout = (STORE / "thanh-toan.html").read_text(encoding="utf-8")
    confirmation = (STORE / "dat-hang-thanh-cong.html").read_text(encoding="utf-8")
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    assert "còn ít nhất 5 sản phẩm khả dụng" in checkout
    assert "tạo đơn bán chưa thanh toán" in checkout
    assert "ghi nhận xuất kho ngay" in checkout
    assert 'data-order-lookup' in confirmation
    assert "salesOrderStatus" in script
    assert "inventoryFulfilled" in script
    assert "function orderButton(product)" in script
    assert "Hết hàng (còn dưới 5)" in script
    assert "product.usableQuantity >= 5 && !product.is_demo && product.price != null" in script


def test_product_details_show_only_catalog_facts_and_mark_missing_fields():
    script = (STORE / "scripts" / "store.js").read_text(encoding="utf-8")
    styles = (STORE / "styles" / "store.css").read_text(encoding="utf-8")
    assert "Chưa được cung cấp trong catalog" in script
    assert "Thành phần ghi trong catalog" in script
    assert "không thay thế nhãn sản phẩm" in script
    assert "Catalog chính thức theo xác nhận quản trị viên" in script
    assert "ownerConfirmedOfficial" in script
    assert "function formatLifeStage" in script
    assert 'const displaySku = (value) => String(value ?? "").replace(/^DEMO-/i, "")' in script
    assert 'if (key === "item_code" || key === "combo_code") return displaySku(value)' in script
    assert '["Mã hàng", displaySku(product.item_code || product.combo_code || product.id)]' in script
    assert "Giá niêm yết · đã gồm VAT 10%" in script
    assert "Giá dữ liệu demo · cần xác nhận" not in script
    assert "Dữ liệu demo · cần cửa hàng xác nhận" not in script
    assert "store-sync-status" not in script
    assert "Đang xem snapshot" not in script
    assert "Live API chưa kết nối" not in script
    assert "Không có liều dùng" not in script
    assert ".product-detail-panel" in styles
