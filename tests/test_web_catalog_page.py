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
        {
            "animals", "pet_detail", "customer_insights",
            "data_catalog", "customer_portal",
        },
    )

    assert page.table.rowCount() == 3
    assert page.summary.text() == (
        "3 trang HTML · 3 trang có lối tắt Python · "
        "22 màn hình Python đã đối chiếu"
    )
    assert page.coverage_table.rowCount() == 22
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

    coverage_rows = {
        page.coverage_table.item(row, 0).text(): row
        for row in range(page.coverage_table.rowCount())
    }
    detail_row = coverage_rows["Chi tiết thú cưng"]
    assert page.coverage_table.item(detail_row, 1).text() == (
        "Trang hỗ trợ/pet_health_report.html"
    )
    assert page.coverage_table.item(detail_row, 2).text() == "Chưa tương đương"
    detail_buttons = page.coverage_table.cellWidget(detail_row, 4).findChildren(
        QPushButton
    )
    assert [button.text() for button in detail_buttons] == ["Mở HTML", "Mở Python"]
    detail_buttons[1].click()
    assert opened_python[-1] == ("pet_detail", 4)

    insights_row = coverage_rows["Khách hàng & dịch vụ"]
    assert page.coverage_table.item(insights_row, 2).text() == "Chưa tương đương"


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
