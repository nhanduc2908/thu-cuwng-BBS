from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from app.ui.web_catalog import page as web_catalog


@pytest.fixture
def application():
    return QApplication.instance() or QApplication([])


def test_web_catalog_lists_pages_and_marks_python_equivalents(
    application, monkeypatch, tmp_path: Path
):
    support = tmp_path / "Trang hỗ trợ" / "Module"
    support.mkdir(parents=True)
    (support / "module_04_pets.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "Trang hỗ trợ" / "data_explorer.html").write_text(
        "<html></html>", encoding="utf-8"
    )
    (tmp_path / "TRrang chính").mkdir()
    (tmp_path / "TRrang chính" / "user_portal.html").write_text(
        "<html></html>", encoding="utf-8"
    )
    monkeypatch.setattr(web_catalog, "HTML_ROOT", tmp_path)
    opened_html: list[str] = []
    opened_python: list[tuple[str, int]] = []

    page = web_catalog.WebCatalogPage(
        opened_html.append,
        lambda route, index: opened_python.append((route, index)),
        {"animals", "data_catalog", "customer_portal"},
    )

    assert page.table.rowCount() == 3
    assert page.summary.text() == "3 trang HTML · 3 trang có lối tắt Python"
    rows_by_path = {
        page.table.item(row, 0).text(): row
        for row in range(page.table.rowCount())
    }
    pets_row = rows_by_path["Trang hỗ trợ/Module/module_04_pets.html"]
    assert page.table.item(pets_row, 3).text() == "Quản lý thú cưng"
    pet_buttons = page.table.cellWidget(pets_row, 4).findChildren(QPushButton)
    assert [button.text() for button in pet_buttons] == ["Mở HTML", "Mở Python"]
    pet_buttons[0].click()
    pet_buttons[1].click()
    assert opened_html == ["/Trang hỗ trợ/Module/module_04_pets.html"]
    assert opened_python == [("animals", 3)]

    portal_row = rows_by_path["TRrang chính/user_portal.html"]
    assert "Cổng khách hàng" in page.table.item(portal_row, 2).text()
    assert page.table.item(portal_row, 3).text() == "Quản lý tài khoản portal"
    portal_buttons = page.table.cellWidget(portal_row, 4).findChildren(QPushButton)
    assert [button.text() for button in portal_buttons] == ["Mở HTML", "Mở Python"]
    portal_buttons[1].click()
    assert opened_python[-1] == ("customer_portal", 21)


def test_web_catalog_hides_python_shortcut_without_view_permission(
    application, monkeypatch, tmp_path: Path
):
    support = tmp_path / "Trang hỗ trợ" / "Module"
    support.mkdir(parents=True)
    (support / "module_04_pets.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(web_catalog, "HTML_ROOT", tmp_path)
    page = web_catalog.WebCatalogPage(lambda _: None, lambda *_: None, set())

    assert page.table.item(0, 3).text() == "Không đủ quyền xem màn hình Python"
    buttons = page.table.cellWidget(0, 4).findChildren(QPushButton)
    assert [button.text() for button in buttons] == ["Mở HTML"]
