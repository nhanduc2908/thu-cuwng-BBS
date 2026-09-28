from app.database import Database
from app.ui.imports.page import ImportsPage


class SuppliersPage(ImportsPage):
    def __init__(self, database: Database) -> None:
        super().__init__(database, focused_section="suppliers")
        self.setWindowTitle("Nhà cung cấp")

    def refresh(self, *_: object) -> None:
        self.refresh_suppliers()
