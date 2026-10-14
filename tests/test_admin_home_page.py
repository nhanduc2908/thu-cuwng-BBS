from PySide6.QtWidgets import QApplication

from app.modules.auth.constants import ROLE_PERMISSIONS
from app.ui.admin_home_page import AdminHomePage, routes_for_permissions


def test_admin_home_shows_only_authorized_internal_function_groups():
    application = QApplication.instance() or QApplication([])
    opened = []
    page = AdminHomePage(
        "Nhân viên bán hàng",
        {"dashboard", "customers", "sales"},
        lambda route, index: opened.append((route, index)),
    )

    assert set(page.section_cards) == {"TỔNG QUAN", "BÁN HÀNG & DỊCH VỤ"}
    assert set(page.route_buttons) == {"dashboard", "customers", "sales"}

    page.route_buttons["sales"].click()
    assert opened == [("sales", 13)]
    page.close()
    application.processEvents()


def test_admin_home_omits_sections_without_permitted_routes():
    application = QApplication.instance() or QApplication([])
    page = AdminHomePage(
        "Chuyên viên báo cáo",
        {"reports"},
        lambda *_: None,
    )

    assert set(page.section_cards) == {"BÁO CÁO & QUẢN TRỊ"}
    assert set(page.route_buttons) == {"reports"}
    page.close()
    application.processEvents()


def test_admin_routes_are_derived_from_staff_permissions_not_customer_roles():
    assert "CUSTOMER" not in ROLE_PERMISSIONS

    sales_routes = routes_for_permissions(ROLE_PERMISSIONS["SALES"])
    assert {"home", "dashboard", "customers", "sales"} <= sales_routes
    assert "sales.request" in ROLE_PERMISSIONS["SALES"]
    assert "sales.manage" not in ROLE_PERMISSIONS["SALES"]
    assert "customer_portal" not in sales_routes

    analyst_routes = routes_for_permissions(ROLE_PERMISSIONS["REPORT_ANALYST"])
    assert {"home", "dashboard", "reports"} <= analyst_routes
    assert "sales" not in analyst_routes
    assert "customer_portal" not in analyst_routes
