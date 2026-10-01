from __future__ import annotations

import sqlite3
from datetime import datetime

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPainter
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.nutrition.recommendation_engine import recommend_foods_for_pet
from app.modules.nutrition.repository import FoodNutritionRepository
from app.ui.common import make_table, set_cell


class PetDetailPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        header = QHBoxLayout()
        self.breadcrumb = QLabel("Trang chủ / Khách hàng / Pet detail")
        self.breadcrumb.setStyleSheet("color: #648071; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header.addWidget(QLabel("Pet detail page", objectName="pageTitle"))
        header.addStretch()
        header.addWidget(self.breadcrumb)
        layout.addLayout(header)
        layout.addWidget(
            QLabel("Xem hồ sơ cá nhân, lịch chăm sóc, chỉ số sức khỏe và lịch sử dịch vụ của từng thú cưng.")
        )

        selector_row = QHBoxLayout()
        selector_row.setSpacing(12)
        selector_row.addWidget(QLabel("Khách hàng:"))
        self.customer_filter = QComboBox()
        self.customer_filter.currentIndexChanged.connect(self._customer_changed)
        selector_row.addWidget(self.customer_filter, 2)
        selector_row.addWidget(QLabel("Thú cưng:"))
        self.pet_filter = QComboBox()
        self.pet_filter.currentIndexChanged.connect(self._pet_changed)
        selector_row.addWidget(self.pet_filter, 2)
        selector_row.addWidget(QLabel("Từ ngày:"))
        self.from_date_filter = QDateEdit(QDate.currentDate())
        self.from_date_filter.setCalendarPopup(True)
        selector_row.addWidget(self.from_date_filter, 1)
        selector_row.addWidget(QLabel("Đến ngày:"))
        self.to_date_filter = QDateEdit(QDate.currentDate())
        self.to_date_filter.setCalendarPopup(True)
        selector_row.addWidget(self.to_date_filter, 1)
        self.filter_button = QPushButton("Lọc dữ liệu")
        self.filter_button.clicked.connect(self._apply_date_filter)
        selector_row.addWidget(self.filter_button)
        self.export_button = QPushButton("Xuất PDF / In")
        self.export_button.clicked.connect(self.export_health_report)
        selector_row.addWidget(self.export_button)
        layout.addLayout(selector_row)

        self.summary_cards = QHBoxLayout()
        self.summary_cards.setSpacing(12)
        self.summary_labels: dict[str, QLabel] = {}
        for label in ("Health status", "Care tasks", "Appointments", "Activity score"):
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(label))
            value = QLabel("0")
            value.setObjectName("statValue")
            card_layout.addWidget(value)
            self.summary_cards.addWidget(card)
            self.summary_labels[label] = value
        layout.addLayout(self.summary_cards)

        detail_panel = QFrame(objectName="profileCard")
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(18, 18, 18, 18)
        detail_layout.setSpacing(12)

        top = QHBoxLayout()
        self.pet_avatar = QLabel("🐾")
        self.pet_avatar.setStyleSheet(
            "font-size: 34px; background: #f7f0df; border-radius: 20px; min-width: 74px; min-height: 74px; qproperty-alignment: AlignCenter;"
        )
        top.addWidget(self.pet_avatar)
        identity = QVBoxLayout()
        self.pet_name = QLabel("-")
        self.pet_name.setStyleSheet("font-size: 20px; font-weight: 700; color: #244b3b;")
        self.pet_badge = QLabel("Bình thường")
        self.pet_badge.setStyleSheet(
            "background: #edf7ee; color: #2d7d42; border-radius: 12px; padding: 5px 10px;"
        )
        identity.addWidget(self.pet_name)
        identity.addWidget(self.pet_badge)
        top.addLayout(identity)
        detail_layout.addLayout(top)

        meta_grid = QGridLayout()
        meta_keys = ["Giống", "Khách hàng", "Cân nặng", "Môi trường", "Tuổi", "Hoạt động"]
        self.meta_values: dict[str, QLabel] = {}
        for index, key in enumerate(meta_keys):
            title = QLabel(f"{key}:")
            title.setStyleSheet("font-weight: 600; color: #31445d;")
            value = QLabel("-")
            meta_grid.addWidget(title, index, 0)
            meta_grid.addWidget(value, index, 1)
            self.meta_values[key] = value
        detail_layout.addLayout(meta_grid)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_text("overview"), "Overview")
        self.tabs.addTab(self._build_tab_text("nutrition"), "Nutrition")
        self.tabs.addTab(self._build_tab_text("health"), "Health")
        self.tabs.addTab(self._build_tab_text("grooming"), "Grooming")
        detail_layout.addWidget(self.tabs)
        layout.addWidget(detail_panel)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(18)

        timeline_panel = QFrame(objectName="profileCard")
        timeline_layout = QVBoxLayout(timeline_panel)
        timeline_layout.setContentsMargins(16, 16, 16, 16)
        timeline_layout.addWidget(QLabel("Care timeline", objectName="pageSubtitle"))
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(12)
        timeline_layout.addWidget(self.timeline_container)
        bottom_row.addWidget(timeline_panel, 2)

        analytics_panel = QFrame(objectName="profileCard")
        analytics_layout = QVBoxLayout(analytics_panel)
        analytics_layout.setContentsMargins(16, 16, 16, 16)
        analytics_layout.addWidget(QLabel("Pet analytics", objectName="pageSubtitle"))
        self.chart_figure = Figure(figsize=(4, 2.8), dpi=100)
        self.chart_axis = self.chart_figure.add_subplot(111)
        self.chart_figure.patch.set_facecolor("#fffdf9")
        self.chart_axis.set_facecolor("#fffdf9")
        self.chart_canvas = FigureCanvas(self.chart_figure)
        analytics_layout.addWidget(self.chart_canvas)
        bottom_row.addWidget(analytics_panel, 1)
        layout.addLayout(bottom_row)

        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(18)

        service_panel = QFrame(objectName="profileCard")
        service_layout = QVBoxLayout(service_panel)
        service_layout.setContentsMargins(16, 16, 16, 16)
        service_layout.addWidget(QLabel("Service history", objectName="pageSubtitle"))
        self.service_history_table = make_table(["Ngày", "Dịch vụ", "Trạng thái", "Giá"])
        service_layout.addWidget(self.service_history_table)
        secondary_row.addWidget(service_panel, 2)

        vaccination_panel = QFrame(objectName="profileCard")
        vaccination_layout = QVBoxLayout(vaccination_panel)
        vaccination_layout.setContentsMargins(16, 16, 16, 16)
        vaccination_layout.addWidget(QLabel("Vaccination record", objectName="pageSubtitle"))
        self.vaccination_table = make_table(["Loại", "Ngày", "Ghi chú", "Trạng thái"])
        vaccination_layout.addWidget(self.vaccination_table)
        secondary_row.addWidget(vaccination_panel, 1)
        layout.addLayout(secondary_row)

    def _build_tab_text(self, key: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel("-")
        label.setWordWrap(True)
        setattr(self, f"{key}_summary", label)
        if key == "nutrition":
            self.nutrition_list = QWidget()
            self.nutrition_list_layout = QVBoxLayout(self.nutrition_list)
            self.nutrition_list_layout.setContentsMargins(0, 0, 0, 0)
            self.nutrition_list_layout.setSpacing(8)
            layout.addWidget(self.nutrition_list)
        layout.addWidget(label)
        return tab

    def refresh(self) -> None:
        customers = self.database.list_customers()
        self.customer_filter.clear()
        self.customer_filter.addItem("Tất cả khách hàng", None)
        for customer in customers:
            self.customer_filter.addItem(str(customer["name"]), int(customer["id"]))
        self.pet_filter.clear()
        all_pets = self.database.customers.list_pets()
        if all_pets:
            self.pet_filter.addItem("Tất cả thú cưng", None)
            for pet in all_pets:
                self.pet_filter.addItem(str(pet["name"]), int(pet["id"]))
        self._customer_changed()

    def _customer_changed(self, *_: object) -> None:
        customer_id = self.customer_filter.currentData()
        if customer_id is None:
            pets = self.database.customers.list_pets()
        else:
            pets = self.database.customers.list_pets(int(customer_id))
        self.pet_filter.clear()
        for pet in pets:
            self.pet_filter.addItem(str(pet["name"]), int(pet["id"]))
        if pets:
            self.pet_filter.setCurrentIndex(0)
            self._pet_changed()
        else:
            self._clear_selection()

    def _pet_changed(self, *_: object) -> None:
        pet_id = self.pet_filter.currentData()
        if pet_id is None:
            self._clear_selection()
            return
        pet = self.database.customers.get_pet(int(pet_id))
        if pet is None:
            self._clear_selection()
            return
        customer = self.database.get_customer(int(pet["customer_id"]))

        self.pet_avatar.setText("🐶" if str(pet["species"]).lower().startswith("chó") else "🐱")
        self.pet_name.setText(f"{pet['name']} · {pet['species']}")
        health_status = pet["health_status"] or "Bình thường"
        self.pet_badge.setText(health_status)
        bg, fg = self._badge_colors(health_status)
        self.pet_badge.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 12px; padding: 5px 10px;"
        )

        self.meta_values["Giống"].setText(str(pet["breed_name"]) or "Chưa xác định")
        self.meta_values["Khách hàng"].setText(str(customer["name"]) if customer else "Chưa gán")
        self.meta_values["Cân nặng"].setText(f"{pet['weight_kg']} kg" if pet["weight_kg"] is not None else "Chưa cập nhật")
        self.meta_values["Môi trường"].setText(str(pet["environment_type"]) or "Trong nhà")
        self.meta_values["Tuổi"].setText(str(pet["birth_date"]) or "Chưa xác định")
        self.meta_values["Hoạt động"].setText(str(pet["activity_level"]) or "Trung bình")

        care_tasks = [item for item in self.database.list_care_tasks() if int(item["animal_id"]) == int(pet["id"])]
        health_records = [item for item in self.database.list_health_records() if int(item["animal_id"]) == int(pet["id"])]
        appointments = [item for item in self.database.list_service_appointments() if str(item["pet_name"]).casefold() == str(pet["name"]).casefold()]

        self.summary_labels["Health status"].setText(health_status)
        self.summary_labels["Care tasks"].setText(str(len(care_tasks)))
        self.summary_labels["Appointments"].setText(str(len(appointments)))
        self.summary_labels["Activity score"].setText(str(min(100, 45 + len(care_tasks) * 10 + len(appointments) * 8)))

        self.breadcrumb.setText(f"Trang chủ / Khách hàng / {customer['name'] if customer else 'Khách hàng'} / {pet['name']}")

        self.overview_summary.setText(
            f"Tên: {pet['name']} | Loài: {pet['species']} | Giống: {pet['breed_name'] or 'Chưa xác định'} | Mức độ hoạt động: {pet['activity_level'] or 'Trung bình'} | Thân trạng: {pet['body_condition'] or 'Bình thường'} | Ghi chú: {pet['notes'] or 'Không có ghi chú'}"
        )
        self.nutrition_summary.setText(
            f"Khuyến nghị dinh dưỡng: ưu tiên chế độ phù hợp với {pet['species']} và mức hoạt động {pet['activity_level'] or 'Trung bình'}. Cân nặng hiện tại: {self.meta_values['Cân nặng'].text()} | Môi trường: {pet['environment_type'] or 'Trong nhà'}"
        )
        self._render_nutrition_recommendations(pet)
        self.health_summary.setText(
            f"Tình trạng sức khỏe: {health_status}. Hồ sơ gần đây: {len(health_records)} lần thăm khám | Theo dõi định kỳ và chú ý trạng thái {pet['body_condition'] or 'Bình thường'}."
        )
        self.grooming_summary.setText(
            f"Chăm sóc cơ bản: chải lông, vệ sinh tai/mắt, kiểm tra da. Mức độ chăm sóc gần đây: {len(care_tasks)}task(s) | Môi trường sống: {pet['environment_type'] or 'Trong nhà'}"
        )

        timeline_rows: list[tuple[str, str, str, str]] = []
        for task in care_tasks:
            status = "Đã hoàn thành" if task["is_completed"] else "Chờ thực hiện"
            timeline_rows.append((str(task["scheduled_at"])[:10], "Care", str(task["title"]), status))
        for record in health_records:
            timeline_rows.append((str(record["examination_date"])[:10], "Health", str(record["health_status"]), str(record["diagnosis"]) or "Theo dõi"))
        for appointment in appointments:
            timeline_rows.append((str(appointment["scheduled_at"])[:10], "Service", str(appointment["package_name"]), str(appointment["status"])))
        timeline_rows.sort(key=lambda item: item[0], reverse=True)

        filtered_rows = []
        start_date = self.from_date_filter.date().toPython()
        end_date = self.to_date_filter.date().toPython()
        for row in timeline_rows:
            event_date = row[0]
            try:
                event_dt = datetime.fromisoformat(event_date)
            except ValueError:
                continue
            if start_date and event_dt.date() < start_date:
                continue
            if end_date and event_dt.date() > end_date:
                continue
            filtered_rows.append(row)
        if not filtered_rows:
            filtered_rows = timeline_rows

        self._render_swimlane_timeline(filtered_rows[:12])

        self.service_history_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments[:8]):
            set_cell(self.service_history_table, row, 0, str(appointment["scheduled_at"])[:10])
            set_cell(self.service_history_table, row, 1, str(appointment["package_name"]))
            set_cell(self.service_history_table, row, 2, str(appointment["status"]))
            set_cell(self.service_history_table, row, 3, f"{float(appointment['total_price'] or 0):,.0f} ₫")

        vaccination_rows = []
        vaccination_status = str(pet["vaccination_status"]).strip() if pet["vaccination_status"] else "Chưa cập nhật"
        vaccination_rows.append(("Tiêm phòng", "-", vaccination_status, "Cập nhật hồ sơ"))
        for record in health_records[:3]:
            diagnosis = str(record["diagnosis"]) or "Theo dõi" 
            if "tiêm" in diagnosis.lower() or "vaccine" in diagnosis.lower():
                vaccination_rows.append(("Khám / kiểm tra", str(record["examination_date"])[:10], diagnosis, "Hoàn tất"))
        self.vaccination_table.setRowCount(len(vaccination_rows))
        for row, (kind, date_value, note, status) in enumerate(vaccination_rows[:6]):
            set_cell(self.vaccination_table, row, 0, kind)
            set_cell(self.vaccination_table, row, 1, date_value)
            set_cell(self.vaccination_table, row, 2, note)
            set_cell(self.vaccination_table, row, 3, status)

        self._render_chart(care_tasks, health_records, appointments)

    def _render_nutrition_recommendations(self, pet: sqlite3.Row) -> None:
        if not hasattr(self, "nutrition_list_layout"):
            return
        while self.nutrition_list_layout.count():
            item = self.nutrition_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        species = "DOG" if str(pet["species"]).lower().startswith("chó") else "CAT"
        weight_kg = pet["weight_kg"] if pet["weight_kg"] is not None else 12.0
        age_months = 24
        try:
            from datetime import date
            if pet["birth_date"]:
                parts = str(pet["birth_date"]).split("-")
                if len(parts) >= 3:
                    year, month, day = map(int, parts[:3])
                    age_months = max(1, (date.today() - date(year, month, day)).days // 30)
        except Exception:
            age_months = 24

        profile = {
            "species": species,
            "age_months": age_months,
            "weight_kg": weight_kg,
            "activity_level": pet["activity_level"] or "MEDIUM",
            "body_condition": pet["body_condition"] or "NORMAL",
            "health_condition": pet["health_status"] or "HEALTHY",
            "allergies": pet["allergies"] or "",
        }
        foods = FoodNutritionRepository(self.database.connection).list_foods_for_species(species, limit=20)
        recommendations = recommend_foods_for_pet(profile, foods, limit=3)
        if not recommendations:
            label = QLabel("Chưa có dữ liệu thức ăn phù hợp cho thú cưng này.")
            self.nutrition_list_layout.addWidget(label)
            return
        for item in recommendations:
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.addWidget(QLabel(f"{item['product_name']} · {item['brand']}"))
            card_layout.addWidget(QLabel(f"Loại: {item['food_type']} · Giai đoạn: {item['life_stage']} · Điểm: {item['nutrition_score']:.1f}"))
            self.nutrition_list_layout.addWidget(card)

    def _render_swimlane_timeline(self, events: list[tuple[str, str, str, str]]) -> None:
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not events:
            empty = QLabel("Không có dữ liệu trong khoảng thời gian đã chọn.")
            self.timeline_layout.addWidget(empty)
            return

        for date_value, kind, title, status in events:
            row = QFrame(objectName="statCard")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 10, 10, 10)
            date_label = QLabel(date_value)
            date_label.setStyleSheet("font-weight: 700; color: #31445d; min-width: 100px;")
            row_layout.addWidget(date_label)

            bar = QFrame()
            bar.setStyleSheet("background: #d7775c; border-radius: 8px; min-width: 8px; min-height: 50px;")
            row_layout.addWidget(bar)

            content = QVBoxLayout()
            content.addWidget(QLabel(kind, styleSheet="font-weight: 700; color: #244b3b;"))
            content.addWidget(QLabel(title, styleSheet="color: #31445d;"))
            status_style = self._status_label_style(status)
            status_label = QLabel(status)
            status_label.setStyleSheet(f"background: {status_style[0]}; color: {status_style[1]}; border-radius: 10px; padding: 4px 8px;")
            content.addWidget(status_label)
            row_layout.addLayout(content)
            self.timeline_layout.addWidget(row)

    @staticmethod
    def _status_label_style(status: str) -> tuple[str, str]:
        normalized = (status or "").lower()
        if "hoàn thành" in normalized or "completed" in normalized:
            return "#edf7ee", "#2d7d42"
        if "chờ" in normalized or "pending" in normalized:
            return "#fff1d8", "#9b5f17"
        if "hủy" in normalized or "cancel" in normalized or "nguy" in normalized:
            return "#fde7e7", "#b33636"
        return "#edf3ff", "#355c49"

    def _apply_date_filter(self) -> None:
        if self.pet_filter.currentData() is not None:
            self._pet_changed()

    def export_health_report(self) -> None:
        pet_id = self.pet_filter.currentData()
        if pet_id is None:
            return
        pet = self.database.customers.get_pet(int(pet_id))
        if pet is None:
            return
        customer = self.database.get_customer(int(pet["customer_id"]))
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            return
        painter = QPainter(printer)
        try:
            painter.setPen(Qt.GlobalColor.black)
            painter.setFont(self.font())
            y = 60
            lines = [
                "PET HEALTH REPORT",
                f"Khách hàng: {customer['name'] if customer else 'Chưa gán'}",
                f"Thú cưng: {pet['name']} ({pet['species']})",
                f"Giống: {pet['breed_name'] or 'Chưa xác định'}",
                f"Cân nặng: {pet['weight_kg']} kg" if pet['weight_kg'] is not None else "Cân nặng: Chưa cập nhật",
                f"Trạng thái: {pet['health_status'] or 'Bình thường'}",
                f"Môi trường: {pet['environment_type'] or 'Trong nhà'}",
                f"Hoạt động: {pet['activity_level'] or 'Trung bình'}",
                f"Ghi chú: {pet['notes'] or 'Không có ghi chú'}",
            ]
            for line in lines:
                painter.drawText(60, y, line)
                y += 28
        finally:
            painter.end()

    def _render_chart(self, care_tasks: list, health_records: list, appointments: list) -> None:
        self.chart_axis.clear()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        care_counts = [0, 0, 0, 0, 0, 0]
        health_counts = [0, 0, 0, 0, 0, 0]
        revenue_counts = [0, 0, 0, 0, 0, 0]
        for task in care_tasks:
            try:
                dt = datetime.fromisoformat(str(task["scheduled_at"]).replace(" ", "T"))
                idx = min(max(dt.month - 1, 0), 5)
                care_counts[idx] += 1
            except (TypeError, ValueError):
                continue
        for record in health_records:
            try:
                dt = datetime.fromisoformat(str(record["examination_date"]).replace(" ", "T"))
                idx = min(max(dt.month - 1, 0), 5)
                health_counts[idx] += 1
            except (TypeError, ValueError):
                continue
        for appointment in appointments:
            try:
                dt = datetime.fromisoformat(str(appointment["scheduled_at"]).replace(" ", "T"))
                idx = min(max(dt.month - 1, 0), 5)
                revenue_counts[idx] += float(appointment["total_price"] or 0) / 1000000
            except (TypeError, ValueError):
                continue
        self.chart_axis.bar(months, care_counts, color="#d9eadb", alpha=0.9, label="Care")
        self.chart_axis.bar(months, health_counts, color="#cfe2ff", alpha=0.8, label="Health")
        self.chart_axis.plot(months, revenue_counts, color="#d7775c", marker="o", linewidth=2.2, label="Revenue (M)")
        self.chart_axis.set_axisbelow(True)
        self.chart_axis.grid(axis="y", linestyle="--", alpha=0.35)
        self.chart_axis.set_title("Pet activity analytics")
        self.chart_axis.legend(loc="upper right")
        self.chart_figure.tight_layout()
        self.chart_canvas.draw()

    @staticmethod
    def _badge_colors(status: str) -> tuple[str, str]:
        normalized = (status or "Bình thường").lower()
        if "theo dõi" in normalized or "warning" in normalized:
            return "#fff1d8", "#9b5f17"
        if "nguy" in normalized or "risk" in normalized or "đang điều trị" in normalized:
            return "#fde7e7", "#b33636"
        return "#edf7ee", "#2d7d42"

    def _clear_selection(self) -> None:
        self.pet_name.setText("-")
        self.pet_avatar.setText("🐾")
        self.pet_badge.setText("Bình thường")
        self.pet_badge.setStyleSheet(
            "background: #edf7ee; color: #2d7d42; border-radius: 12px; padding: 5px 10px;"
        )
        for key in self.meta_values:
            self.meta_values[key].setText("-")
        for key in ("overview", "nutrition", "health", "grooming"):
            getattr(self, f"{key}_summary").setText("-")
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.timeline_layout.addWidget(QLabel("Không có dữ liệu trong khoảng thời gian đã chọn."))
        self.service_history_table.setRowCount(0)
        self.vaccination_table.setRowCount(0)
        self.chart_axis.clear()
        self.chart_axis.text(0.5, 0.5, "Không có dữ liệu", ha="center", va="center")
        self.chart_axis.set_axis_off()
        self.chart_figure.tight_layout()
        self.chart_canvas.draw()
