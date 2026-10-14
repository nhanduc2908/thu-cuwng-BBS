from PySide6.QtWidgets import QApplication

from app.database import Database
from app.ui.dashboard.page import DashboardPage, display_animal_code


def test_dashboard_displays_pet_codes_without_demo_prefix(tmp_path):
    application = QApplication.instance() or QApplication([])
    database = Database(tmp_path / "dashboard.db")
    try:
        with database.connection:
            database.connection.execute(
                """
                INSERT INTO animals (animal_code, name, species)
                VALUES ('DEMO-PET-001', 'Milo', 'Chó')
                """
            )

        page = DashboardPage(database)
        page.refresh()

        assert page.table.rowCount() == 1
        assert page.table.item(0, 0).text() == "PET-001"
        assert database.connection.execute(
            "SELECT animal_code FROM animals WHERE name = 'Milo'"
        ).fetchone()["animal_code"] == "DEMO-PET-001"
        page.close()
    finally:
        database.close()
        application.processEvents()


def test_animal_code_display_only_removes_leading_demo_prefix():
    assert display_animal_code("PET-001") == "PET-001"
    assert display_animal_code("demo-PET-001") == "demo-PET-001"
