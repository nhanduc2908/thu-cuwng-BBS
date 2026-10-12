from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = PROJECT_ROOT / "HTML" / "Trang thông số của các sản phẩm"
REFERENCE_PAGES = (
    "index.html",
    "thuong-hieu.html",
    "nutrition-standards.html",
    "aafco-guide.html",
    "fediaf-europe-guide.html",
    "dog-breed-standards.html",
    "cat-breed-standards.html",
    "nutrient-reference-40.html",
)
SHARED_DESTINATIONS = {
    "index.html",
    "thuong-hieu.html",
    "nutrition-standards.html",
    "aafco-guide.html",
    "fediaf-europe-guide.html",
    "dog-breed-standards.html",
    "cat-breed-standards.html",
    "nutrient-reference-40.html",
}


class NavigationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_navigation = False
        self.navigation_links = set()
        self.all_links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "nav":
            self.in_navigation = True
        if tag == "a" and attributes.get("href"):
            href = attributes["href"]
            self.all_links.append(href)
            if self.in_navigation:
                self.navigation_links.add(urlsplit(href).path)

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_navigation = False


def test_reference_pages_share_complete_navigation():
    for relative_path in REFERENCE_PAGES:
        parser = NavigationParser()
        parser.feed((REFERENCE_ROOT / relative_path).read_text(encoding="utf-8"))

        assert SHARED_DESTINATIONS <= parser.navigation_links, relative_path


def test_reference_pages_have_no_broken_local_links():
    for relative_path in REFERENCE_PAGES:
        source_path = REFERENCE_ROOT / relative_path
        parser = NavigationParser()
        parser.feed(source_path.read_text(encoding="utf-8"))

        for href in parser.all_links:
            target_url = urlsplit(href)
            if target_url.scheme or target_url.netloc or not target_url.path:
                continue
            target_path = (source_path.parent / unquote(target_url.path)).resolve()
            assert target_path.is_relative_to(PROJECT_ROOT) and target_path.exists(), (
                relative_path,
                href,
            )
