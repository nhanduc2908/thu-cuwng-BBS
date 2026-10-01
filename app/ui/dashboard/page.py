import sqlite3

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.nutrition.recommendation_engine import recommend_foods_for_pet
from app.modules.nutrition.repository import FoodNutritionRepository
from app.ui.common import STATUS_LABELS, make_table, set_cell


class DashboardPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Tổng quan cửa hàng", objectName="pageTitle"))
        top_row.addStretch()
        self.header_action = QPushButton("+ Tạo báo cáo nhanh", objectName="primaryButton")
        self.header_action.clicked.connect(self._show_quick_report)
        top_row.addWidget(self.header_action)
        layout.addLayout(top_row)
        layout.addWidget(
            QLabel("Theo dõi nhanh doanh thu, thú cưng, chăm sóc và gợi ý dinh dưỡng.")
        )

        self.cards: dict[str, QLabel] = {}
        cards_layout = QHBoxLayout()
        for key, title, color in (
            ("TOTAL", "Tổng động vật", "#265d50"),
            ("AVAILABLE", "Đang bán", "#287b68"),
            ("SOLD", "Đã bán", "#5967a7"),
            ("TREATMENT", "Đang điều trị", "#bd7629"),
        ):
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(title))
            value = QLabel("0", objectName="statValue")
            value.setStyleSheet(f"color: {color};")
            card_layout.addWidget(value)
            self.cards[key] = value
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)
        self.featured_container = QWidget()
        self.featured_layout = QVBoxLayout(self.featured_container)
        self.featured_layout.setContentsMargins(0, 0, 0, 0)
        self.featured_layout.setSpacing(12)
        self.featured_layout.addWidget(QLabel("Thú cưng nổi bật", objectName="sectionTitle"))

        self.featured_pets_area = QWidget()
        self.featured_pets_layout = QHBoxLayout(self.featured_pets_area)
        self.featured_pets_layout.setContentsMargins(0, 0, 0, 0)
        self.featured_pets_layout.setSpacing(12)
        self.featured_layout.addWidget(self.featured_pets_area)

        detail_box = QFrame(objectName="profileCard")
        detail_layout = QVBoxLayout(detail_box)
        detail_layout.setContentsMargins(18, 18, 18, 18)
        detail_layout.setSpacing(12)
        detail_layout.addWidget(QLabel("Pet detail panel", objectName="pageSubtitle"))

        self.pet_header = QHBoxLayout()
        self.pet_avatar = QLabel("🐾")
        self.pet_avatar.setStyleSheet(
            "font-size: 32px; background: #f7f0df; border-radius: 18px; min-width: 62px; min-height: 62px; qproperty-alignment: AlignCenter;"
        )
        self.pet_header.addWidget(self.pet_avatar)
        self.pet_identity = QVBoxLayout()
        self.pet_detail_name = QLabel("-")
        self.pet_detail_name.setStyleSheet("font-size: 18px; font-weight: 700; color: #244b3b;")
        self.pet_badge = QLabel("Bình thường")
        self.pet_badge.setStyleSheet(
            "background: #edf7ee; color: #2d7d42; border-radius: 12px; padding: 5px 10px;"
        )
        self.pet_identity.addWidget(self.pet_detail_name)
        self.pet_identity.addWidget(self.pet_badge)
        self.pet_header.addLayout(self.pet_identity)
        detail_layout.addLayout(self.pet_header)

        self.pet_detail_tabs = QTabWidget()
        self.pet_detail_tabs.setObjectName("petDetailTabs")
        self.pet_detail_tabs.addTab(self._build_pet_tab_overview(), "Overview")
        self.pet_detail_tabs.addTab(self._build_pet_tab_nutrition(), "Nutrition")
        self.pet_detail_tabs.addTab(self._build_pet_tab_health(), "Health")
        self.pet_detail_tabs.addTab(self._build_pet_tab_grooming(), "Grooming")
        detail_layout.addWidget(self.pet_detail_tabs)

        content_row.addWidget(self.featured_container, 3)
        content_row.addWidget(detail_box, 2)
        layout.addLayout(content_row)

        analytics_row = QHBoxLayout()
        analytics_row.setSpacing(18)
        analytics_row.addWidget(self._build_analytics_panel(), 2)
        analytics_row.addWidget(self._build_activity_feed(), 1)
        layout.addLayout(analytics_row)

        self.recommendation_panel = self._build_recommendation_panel()
        layout.addWidget(self.recommendation_panel)

        self.customer_overview_panel = self._build_customer_overview_panel()
        layout.addWidget(self.customer_overview_panel)

        layout.addWidget(QLabel("Động vật mới cập nhật", objectName="sectionTitle"))
        self.table = make_table(["Mã", "Tên", "Loài", "Trạng thái", "Ngày tạo"])
        layout.addWidget(self.table)
        layout.addStretch()

    def _build_pet_tab_overview(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        self.overview_meta = QLabel("-")
        self.overview_meta.setWordWrap(True)
        self.overview_summary = QLabel("-")
        self.overview_summary.setWordWrap(True)
        layout.addWidget(QLabel("Thông tin cơ bản"))
        layout.addWidget(self.overview_meta)
        layout.addWidget(QLabel("Tóm tắt chăm sóc"))
        layout.addWidget(self.overview_summary)
        return tab

    def _build_pet_tab_nutrition(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        self.nutrition_summary = QLabel("-")
        self.nutrition_summary.setWordWrap(True)
        layout.addWidget(self.nutrition_summary)
        return tab

    def _build_pet_tab_health(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        self.health_summary = QLabel("-")
        self.health_summary.setWordWrap(True)
        layout.addWidget(self.health_summary)
        return tab

    def _build_pet_tab_grooming(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        self.grooming_summary = QLabel("-")
        self.grooming_summary.setWordWrap(True)
        layout.addWidget(self.grooming_summary)
        return tab

    def _build_analytics_panel(self) -> QWidget:
        panel = QFrame(objectName="profileCard")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.addWidget(QLabel("Dashboard analytics", objectName="pageSubtitle"))

        figure = Figure(figsize=(4, 2.5), dpi=100)
        axis = figure.add_subplot(111)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        values = [55, 68, 63, 76, 81, 92]
        axis.bar(months, values, color="#d9eadb")
        axis.set_ylim(0, 100)
        axis.set_axisbelow(True)
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_title("Service satisfaction", fontsize=9)
        axis.set_facecolor("#fffdf9")
        figure.patch.set_facecolor("#fffdf9")
        canvas = FigureCanvas(figure)
        panel_layout.addWidget(canvas)

        insights = QWidget()
        insight_layout = QHBoxLayout(insights)
        insight_layout.setContentsMargins(0, 0, 0, 0)
        for title, value, tone in (
            ("Chăm sóc", "91%", "#2d7d42"),
            ("Dinh dưỡng", "88%", "#5976b8"),
            ("Khách hàng", "76%", "#9b5f17"),
        ):
            box = QFrame(objectName="statCard")
            inner = QVBoxLayout(box)
            inner.addWidget(QLabel(value, objectName="statValue"))
            inner.addWidget(QLabel(title))
            box.setStyleSheet(f"{box.styleSheet()} QFrame#statCard {{ border-color: {tone}; }}")
            insight_layout.addWidget(box)
        panel_layout.addWidget(insights)
        return panel

    def _build_recommendation_panel(self) -> QWidget:
        panel = QFrame(objectName="profileCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Nutrition recommendation", objectName="pageSubtitle"))

        self.recommendation_items = QWidget()
        self.recommendation_layout = QVBoxLayout(self.recommendation_items)
        self.recommendation_layout.setContentsMargins(0, 0, 0, 0)
        self.recommendation_layout.setSpacing(8)
        layout.addWidget(self.recommendation_items)
        return panel

    def _build_customer_overview_panel(self) -> QWidget:
        panel = QFrame(objectName="profileCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Customer & service overview", objectName="pageSubtitle"))

        self.customer_overview_label = QLabel("Chưa có dữ liệu khách hàng.")
        self.customer_overview_label.setWordWrap(True)
        layout.addWidget(self.customer_overview_label)
        return panel
        return panel

    def _build_activity_feed(self) -> QWidget:
        panel = QFrame(objectName="profileCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(QLabel("Activity feed", objectName="pageSubtitle"))
        for text, time_text in (
            ("Milo đã hoàn thành lịch khám định kỳ", "08:40"),
            ("Sữa dinh dưỡng mới được gợi ý cho Luna", "09:15"),
            ("Khách hàng A. Tran đã đặt lịch tắm", "11:05"),
            ("Duyệt lịch chải lông tuần này", "14:20"),
        ):
            item = QFrame(objectName="statCard")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(10, 10, 10, 10)
            item_layout.addWidget(QLabel(text))
            item_layout.addWidget(QLabel(time_text))
            layout.addWidget(item)
        return panel

    def _show_pet_action(self, action: str) -> None:
        pet_name = self.pet_detail_name.text().split(" — ", 1)[0] if self.pet_detail_name.text() else "Thú cưng"
        QMessageBox.information(
            self,
            "Hành động nhanh",
            f"{pet_name}: đang mở tính năng {action} trong luồng chăm sóc thú cưng.",
        )

    def _show_quick_report(self) -> None:
        QMessageBox.information(
            self,
            "Báo cáo nhanh",
            "Hệ thống đang chuẩn bị báo cáo tổng hợp cho doanh thu, thú cưng và chăm sóc trong ngày.",
        )

    def _status_styles(self, status: str) -> tuple[str, str]:
        normalized = (status or "Bình thường").strip().lower()
        if "cần theo dõi" in normalized or "warning" in normalized:
            return ("#fff1d8", "#9b5f17")
        if "xấu" in normalized or "risk" in normalized or "cấp" in normalized:
            return ("#fde7e7", "#b33636")
        return ("#edf7ee", "#2d7d42")

    def _render_featured_pets(self) -> None:
        while self.featured_pets_layout.count():
            item = self.featured_pets_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        pets = self.database.customers.list_pets()
        featured = sorted(
            pets,
            key=lambda pet: (pet["created_at"], pet["id"]),
            reverse=True,
        )[:4]

        if not featured:
            placeholder = QFrame(objectName="statCard")
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(16, 16, 16, 16)
            placeholder_layout.addWidget(QLabel("Chưa có thú cưng nào."))
            self.featured_pets_layout.addWidget(placeholder)
            return

        for pet in featured:
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(8)

            avatar_text = "🐶" if pet["species"].lower().startswith("chó") else "🐱"
            avatar = QLabel(avatar_text)
            avatar.setStyleSheet(
                "font-size: 28px; background: #f4efe5; border-radius: 18px; min-width: 52px; min-height: 52px; qproperty-alignment: AlignCenter;"
            )
            card_layout.addWidget(avatar)

            name = QLabel(str(pet["name"]))
            name.setStyleSheet("font-weight: 700; font-size: 15px; color: #233d36;")
            card_layout.addWidget(name)

            customer = self.database.get_customer(int(pet["customer_id"]))
            customer_name = customer["name"] if customer else "Khách hàng chưa gán"
            meta = QLabel(f"{pet['species']} · {pet['breed_name'] or 'Chưa xác định'}")
            meta.setWordWrap(True)
            card_layout.addWidget(meta)
            card_layout.addWidget(QLabel(f"Chủ nuôi: {customer_name}"))
            health_status = pet["health_status"] or "Bình thường"
            card_layout.addWidget(QLabel(f"Tình trạng: {health_status}"))

            badge = QLabel("Nổi bật")
            badge.setStyleSheet(
                "background: #fff1d8; color: #9b5f17; border-radius: 10px; padding: 4px 8px;"
            )
            card_layout.addWidget(badge)

            action_layout = QHBoxLayout()
            for action_label in ("Nutrition", "Health", "Grooming"):
                button = QPushButton(action_label)
                button.clicked.connect(
                    lambda _, name=str(pet["name"]), action=action_label: self._show_action_for_pet(name, action)
                )
                action_layout.addWidget(button)
            card_layout.addLayout(action_layout)
            self.featured_pets_layout.addWidget(card)

        selected = featured[0]
        self._update_pet_detail(selected)

    def _update_pet_detail(self, pet: sqlite3.Row) -> None:
        self.pet_detail_name.setText(f"{pet['name']} — {pet['species']}")
        breed = pet["breed_name"] or "Chưa xác định"
        weight = pet["weight_kg"] if pet["weight_kg"] is not None else "Chưa cập nhật"
        health_status = pet["health_status"] or "Bình thường"
        self.pet_badge.setText(health_status)
        bg, fg = self._status_styles(health_status)
        self.pet_badge.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 12px; padding: 5px 10px;"
        )
        self.pet_avatar.setText("🐶" if pet["species"].lower().startswith("chó") else "🐱")

        care_tasks = self.database.list_care_tasks()
        related_care = [task for task in care_tasks if int(task["animal_id"]) == int(pet["id"])][:3]
        care_text = ", ".join(
            f"{task['title']} ({task['scheduled_at'][:10]})" for task in related_care
        ) if related_care else "Chưa có lịch chăm sóc gần đây"

        health_records = self.database.list_health_records()
        related_health = [record for record in health_records if int(record["animal_id"]) == int(pet["id"])][:3]
        health_text = ", ".join(
            f"{record['health_status']} ({record['examination_date']})" for record in related_health
        ) if related_health else "Chưa có hồ sơ sức khỏe gần đây"

        appointments = self.database.list_service_appointments()
        related_appointments = [
            appointment for appointment in appointments if appointment["pet_name"].casefold() == str(pet["name"]).casefold()
        ][:3]
        appointment_text = ", ".join(
            f"{appointment['status']} ({appointment['scheduled_at'][:10]})" for appointment in related_appointments
        ) if related_appointments else "Chưa có lịch dịch vụ"

        self.overview_meta.setText(
            f"Giống: {breed} | Sinh nhật: {pet['birth_date'] or 'Chưa xác định'} | Cân nặng: {weight} kg | Môi trường: {pet['environment_type']}"
        )
        self.overview_summary.setText(
            f"Hoạt động: {pet['activity_level']} | Tình trạng sức khỏe: {health_status} | Ghi chú: {pet['notes'] or 'Không có ghi chú'} | Lịch chăm sóc: {care_text}"
        )
        self.nutrition_summary.setText(
            f"Khuyến nghị dinh dưỡng cho {pet['name']}: ưu tiên chế độ phù hợp với loài {pet['species']}, cân đối lượng calo và protein theo mức hoạt động {pet['activity_level']}. | Lịch sử sức khỏe: {health_text}"
        )
        self.health_summary.setText(
            f"Theo dõi sức khỏe: {health_status}. Nên kiểm tra định kỳ, lưu ý trạng thái {pet['body_condition']} và môi trường sống {pet['environment_type']}. | Hồ sơ gần đây: {health_text}"
        )
        self.grooming_summary.setText(
            f"Lịch chăm sóc: tắm, chải lông và kiểm tra mắt/ tai theo định kỳ. Mức độ cần chú ý: {pet['activity_level']} và môi trường {pet['environment_type']}. | Lịch dịch vụ: {appointment_text}"
        )
        self._render_recommendations(pet)

    def _render_recommendations(self, pet: sqlite3.Row) -> None:
        while self.recommendation_layout.count():
            item = self.recommendation_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        species = "DOG" if str(pet["species"]).lower().startswith("chó") else "CAT"
        age_months = 24
        try:
            if pet["birth_date"]:
                from datetime import date
                birth_date = pet["birth_date"]
                if isinstance(birth_date, str) and birth_date:
                    year, month, day = map(int, birth_date.split("-")[:3])
                    birthday = date(year, month, day)
                    age_months = max(1, (date.today() - birthday).days // 30)
        except Exception:
            age_months = 24

        profile = {
            "species": species,
            "age_months": age_months,
            "weight_kg": pet["weight_kg"] if pet["weight_kg"] is not None else 12.0,
            "activity_level": pet["activity_level"] or "MEDIUM",
            "body_condition": pet["body_condition"] or "NORMAL",
            "health_condition": pet["health_status"] or "HEALTHY",
            "allergies": pet["allergies"] or "",
        }
        repo = FoodNutritionRepository(self.database.connection)
        foods = repo.list_foods_for_species(species, limit=30)
        recommendations = recommend_foods_for_pet(profile, foods, limit=3)

        if not recommendations:
            placeholder = QLabel("Chưa có dữ liệu thức ăn phù hợp cho thú cưng này.")
            self.recommendation_layout.addWidget(placeholder)
            return

        for item in recommendations:
            row = QFrame(objectName="statCard")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.addWidget(QLabel(f"{item['product_name']} · {item['brand']}"))
            row_layout.addWidget(QLabel(f"Loại: {item['food_type']} · Giai đoạn: {item['life_stage']} · Điểm: {item['nutrition_score']:.1f}"))
            self.recommendation_layout.addWidget(row)

    def refresh(self) -> None:
        counts = self.database.dashboard_counts()
        for key, label in self.cards.items():
            label.setText(str(counts[key]))
        self._render_featured_pets()
        customers = self.database.list_customers()
        pets = self.database.customers.list_pets()
        appointments = self.database.list_service_appointments()
        customer_summary = (
            f"Khách hàng hoạt động: {len(customers)} | Thú cưng đang chăm sóc: {len(pets)} | "
            f"Lịch hẹn trong hệ thống: {len(appointments)} | "
            f"Doanh thu: {sum(float(item['total_price'] or 0) for item in appointments):,.0f} ₫"
        )
        self.customer_overview_label.setText(customer_summary)
        animals = self.database.recent_animals()
        self.table.setRowCount(len(animals))
        for row_number, animal in enumerate(animals):
            set_cell(self.table, row_number, 0, animal["animal_code"])
            set_cell(self.table, row_number, 1, animal["name"])
            set_cell(self.table, row_number, 2, animal["species"])
            set_cell(self.table, row_number, 3, STATUS_LABELS[animal["status"]])
            set_cell(self.table, row_number, 4, animal["created_at"][:10])
