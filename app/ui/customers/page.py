from app.database import Database
from app.ui.sales.page import SalesPage


class CustomersPage(SalesPage):
    def __init__(self, database: Database) -> None:
        super().__init__(database, focused_section="customers")
        self.setWindowTitle("Khách hàng")

    def refresh(self) -> None:
        self.refresh_customers()
