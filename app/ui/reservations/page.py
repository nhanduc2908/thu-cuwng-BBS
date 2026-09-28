from app.database import Database
from app.ui.sales.page import SalesPage


class ReservationsPage(SalesPage):
    def __init__(self, database: Database) -> None:
        super().__init__(database, focused_section="reservations")
        self.setWindowTitle("Đặt trước và giữ chỗ")

    def refresh(self) -> None:
        self.refresh_reservations()
