from types import SimpleNamespace

from PySide6.QtGui import QDesktopServices

from app.ui.main_window import MainWindow


def test_main_window_opens_storefront_from_the_local_bridge(monkeypatch):
    opened_urls = []
    monkeypatch.setattr(
        QDesktopServices,
        "openUrl",
        lambda url: opened_urls.append(
            url.toEncoded().data().decode("ascii")
        ) or True,
    )
    MainWindow.open_web_page(
        SimpleNamespace(web_base_url="http://127.0.0.1:8767"),
        "/Web bán hàng/index.html",
    )

    assert opened_urls == [
        "http://127.0.0.1:8767/Web%20b%C3%A1n%20h%C3%A0ng/index.html"
    ]
