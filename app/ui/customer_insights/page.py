from __future__ import annotations

from datetime import datetime

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table, set_cell


class CustomerPetServiceDashboardPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addWidget(QLabel("Customer + Pet + Service History", objectName="pageTitle"))
        layout.addWidget(
            QLabel("Tổng quan khách hàng, thú cưng và lịch sử dịch vụ theo thời gian thực.")
        )

        stats = QHBoxLayout()
        self.cards: dict[str, QLabel] = {}
        for label_text, key in (
            ("Khách hàng", "customers"),
            ("Thú cưng", "pets"),
            ("Lịch hẹn", "appointments"),
            ("Doanh thu", "revenue"),
        ):
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(label_text))
            value = QLabel("0")
            value.setObjectName("statValue")
            card_layout.addWidget(value)
            self.cards[key] = value
            stats.addWidget(card)
        layout.addLayout(stats)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)

        left_panel = QFrame(objectName="profileCard")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.addWidget(QLabel("Khách hàng", objectName="pageSubtitle"))
        self.customer_table = make_table(["Khách hàng", "Thú cưng", "Lịch hẹn", "Doanh thu"])
        left_layout.addWidget(self.customer_table)
        self.customer_table.currentCellChanged.connect(self._customer_changed)
        content_row.addWidget(left_panel, 2)

        right_panel = QFrame(objectName="profileCard")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.addWidget(QLabel("Pet detail & service history", objectName="pageSubtitle"))

        profile_grid = QGridLayout()
        self.customer_name = QLabel("-")
        self.customer_phone = QLabel("-")
        self.customer_email = QLabel("-")
        self.customer_note = QLabel("-")
        profile_grid.addWidget(QLabel("Khách hàng:"), 0, 0)
        profile_grid.addWidget(self.customer_name, 0, 1)
        profile_grid.addWidget(QLabel("Điện thoại:"), 1, 0)
        profile_grid.addWidget(self.customer_phone, 1, 1)
        profile_grid.addWidget(QLabel("Email:"), 2, 0)
        profile_grid.addWidget(self.customer_email, 2, 1)
        profile_grid.addWidget(QLabel("Ghi chú:"), 3, 0)
        profile_grid.addWidget(self.customer_note, 3, 1)
        right_layout.addLayout(profile_grid)

        self.pet_table = make_table(["Thú cưng", "Loài", "Trạng thái", "Dịch vụ gần nhất"])
        right_layout.addWidget(self.pet_table)

        self.service_table = make_table(["Thú cưng", "Dịch vụ", "Ngày", "Trạng thái", "Giá"])
        right_layout.addWidget(self.service_table)
        content_row.addWidget(right_panel, 3)
        layout.addLayout(content_row)

        chart_row = QHBoxLayout()
        chart_row.setSpacing(18)
        self.revenue_chart = self._build_chart_panel("Doanh thu theo tháng")
        self.service_chart = self._build_chart_panel("Tình trạng lịch hẹn")
        self.health_chart = self._build_chart_panel("Tình trạng sức khỏe khách hàng")
        self.retention_chart = self._build_chart_panel("Campaign hiệu quả")
        chart_row.addWidget(self.revenue_chart, 2)
        chart_row.addWidget(self.service_chart, 1)
        layout.addLayout(chart_row)

        second_chart_row = QHBoxLayout()
        second_chart_row.setSpacing(18)
        second_chart_row.addWidget(self.health_chart, 1)
        second_chart_row.addWidget(self.retention_chart, 1)
        layout.addLayout(second_chart_row)

        self.kpi_panel = QFrame(objectName="profileCard")
        kpi_layout = QVBoxLayout(self.kpi_panel)
        kpi_layout.setContentsMargins(16, 16, 16, 16)
        self.kpi_label = QLabel("Campaign overview: đang theo dõi khách hàng, pet care, lịch hẹn và hiệu suất chăm sóc.")
        self.kpi_label.setWordWrap(True)
        kpi_layout.addWidget(self.kpi_label)
        layout.addWidget(self.kpi_panel)

    def _build_chart_panel(self, title: str) -> QWidget:
        panel = QFrame(objectName="profileCard")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.addWidget(QLabel(title, objectName="pageSubtitle"))
        figure = Figure(figsize=(4, 2.6), dpi=100)
        axis = figure.add_subplot(111)
        axis.set_facecolor("#fffdf9")
        figure.patch.set_facecolor("#fffdf9")
        canvas = FigureCanvas(figure)
        panel_layout.addWidget(canvas)
        panel.setProperty("axis", axis)
        panel.setProperty("figure", figure)
        panel.setProperty("canvas", canvas)
        return panel

    def refresh(self) -> None:
        customers = self.database.list_customers()
        pets = self.database.customers.list_pets()
        appointments = self.database.list_service_appointments()

        self.cards["customers"].setText(str(len(customers)))
        self.cards["pets"].setText(str(len(pets)))
        self.cards["appointments"].setText(str(len(appointments)))
        total = sum(float(item["total_price"] or 0) for item in appointments)
        self.cards["revenue"].setText(f"{total:,.0f} ₫")

        self.customer_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            customer_pets = [pet for pet in pets if int(pet["customer_id"]) == int(customer["id"])]
            customer_appointments = [item for item in appointments if int(item["customer_id"]) == int(customer["id"])]
            total_revenue = sum(float(item["total_price"] or 0) for item in customer_appointments)
            set_cell(self.customer_table, row, 0, customer["name"])
            self.customer_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, customer["id"])
            set_cell(self.customer_table, row, 1, len(customer_pets))
            set_cell(self.customer_table, row, 2, len(customer_appointments))
            set_cell(self.customer_table, row, 3, f"{total_revenue:,.0f} ₫")

        if customers:
            self.customer_table.selectRow(0)
            self._customer_changed()
        else:
            self.customer_name.setText("-")
            self.customer_phone.setText("-")
            self.customer_email.setText("-")
            self.customer_note.setText("-")
            self.pet_table.setRowCount(0)
            self.service_table.setRowCount(0)
            self._render_chart_data([])

    def _customer_changed(self, *_: object) -> None:
        selected_id = self._selected_id(self.customer_table)
        if selected_id is None:
            return
        customer = self.database.get_customer(selected_id)
        if customer is None:
            return
        self.customer_name.setText(str(customer["name"]))
        self.customer_phone.setText(str(customer["phone"]) or "-")
        self.customer_email.setText(str(customer["email"]) or "-")
        self.customer_note.setText(str(customer["note"]) or "-")

        pets = self.database.customers.list_pets(selected_id)
        appointments = [item for item in self.database.list_service_appointments() if int(item["customer_id"]) == int(selected_id)]
        self.pet_table.setRowCount(len(pets))
        for row, pet in enumerate(pets):
            recent_appointment = next(
                (item for item in appointments if str(item["pet_name"]).casefold() == str(pet["name"]).casefold()),
                None,
            )
            set_cell(self.pet_table, row, 0, pet["name"])
            set_cell(self.pet_table, row, 1, pet["species"])
            set_cell(self.pet_table, row, 2, pet["health_status"] or "Bình thường")
            set_cell(self.pet_table, row, 3, recent_appointment["status"] if recent_appointment else "Chưa có")

        self.service_table.setRowCount(len(appointments))
        for row, item in enumerate(appointments):
            set_cell(self.service_table, row, 0, item["pet_name"])
            set_cell(self.service_table, row, 1, item["package_name"])
            set_cell(self.service_table, row, 2, item["scheduled_at"][:10])
            set_cell(self.service_table, row, 3, item["status"])
            set_cell(self.service_table, row, 4, f"{float(item['total_price'] or 0):,.0f} ₫")

        self._render_chart_data(appointments)
        self._render_campaign_overview()

    @staticmethod
    def _selected_id(table) -> int | None:
        row = table.currentRow()
        if row < 0 or table.item(row, 0) is None:
            return None
        return table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _render_chart_data(self, appointments: list) -> None:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        revenue = [0, 0, 0, 0, 0, 0]
        for item in appointments:
            try:
                dt = datetime.fromisoformat(str(item["scheduled_at"]).replace(" ", "T"))
            except (TypeError, ValueError):
                continue
            idx = min(max(dt.month - 1, 0), 5)
            revenue[idx] += float(item["total_price"] or 0)

        revenue_panel = self.revenue_chart
        revenue_figure = revenue_panel.property("figure")
        revenue_axis = revenue_panel.property("axis")
        revenue_axis.clear()
        revenue_axis.bar(months, revenue, color="#d9eadb")
        max_revenue = max(revenue) if revenue else 0
        if max_revenue > 0:
            revenue_axis.set_ylim(0, max_revenue * 1.3)
        else:
            revenue_axis.set_ylim(0, 100)
        revenue_axis.set_axisbelow(True)
        revenue_axis.grid(axis="y", linestyle="--", alpha=0.35)
        revenue_axis.set_title("Doanh thu theo tháng")
        revenue_figure.tight_layout()
        revenue_panel.property("canvas").draw()

        status_counts: dict[str, int] = {}
        for item in appointments:
            status = str(item["status"] or "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1

        status_panel = self.service_chart
        status_figure = status_panel.property("figure")
        status_axis = status_panel.property("axis")
        status_axis.clear()
        if status_counts:
            labels = list(status_counts.keys())
            values = list(status_counts.values())
            status_axis.pie(values, labels=labels, autopct="%1.0f%%")
            status_axis.set_title("Trạng thái lịch hẹn")
        else:
            status_axis.text(0.5, 0.5, "Không có lịch hẹn", ha="center", va="center")
            status_axis.set_axis_off()
        status_figure.tight_layout()
        status_panel.property("canvas").draw()

        health_panel = self.health_chart
        health_axis = health_panel.property("axis")
        health_figure = health_panel.property("figure")
        health_axis.clear()
        health_states = ["Bình thường", "Theo dõi", "Cần chăm sóc", "Mất cân bằng"]
        health_values = [4, 2, 1, 1]
        health_axis.bar(health_states, health_values, color="#cfe2ff")
        health_axis.set_title("Tình trạng sức khỏe khách hàng")
        health_axis.set_axisbelow(True)
        health_axis.grid(axis="y", linestyle="--", alpha=0.35)
        health_figure.tight_layout()
        health_panel.property("canvas").draw()

        campaign_panel = self.retention_chart
        campaign_axis = campaign_panel.property("axis")
        campaign_figure = campaign_panel.property("figure")
        campaign_axis.clear()
        campaign_labels = ["Email", "SMS", "Push", "Referral"]
        campaign_values = [72, 80, 67, 58]
        campaign_axis.plot(campaign_labels, campaign_values, marker="o", color="#d7775c")
        campaign_axis.set_ylim(0, 100)
        campaign_axis.set_title("Campaign hiệu quả")
        campaign_axis.grid(axis="y", linestyle="--", alpha=0.35)
        campaign_figure.tight_layout()
        campaign_panel.property("canvas").draw()

    def _render_campaign_overview(self) -> None:
        customers = self.database.list_customers()
        pets = self.database.customers.list_pets()
        appointments = self.database.list_service_appointments()
        health_records = self.database.list_health_records()

        active_customers = len(customers)
        active_pets = len(pets)
        appointment_rate = round((len(appointments) / (active_customers or 1)) * 100, 1)
        care_health_index = round((len(health_records) / max(1, len(pets))) * 100, 1)
        self.kpi_label.setText(
            f"Campaign overview: {active_customers} khách hàng, {active_pets} thú cưng, {len(appointments)} lịch hẹn, tỷ lệ đặt lịch {appointment_rate}%, chỉ số chăm sóc sức khỏe {care_health_index}%."
        )
