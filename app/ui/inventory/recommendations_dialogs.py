import json
import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.recommendations.constants import (
    RECOMMENDATION_AGE_GROUPS,
    RECOMMENDATION_AGE_LABELS,
    RECOMMENDATION_CATEGORIES,
    RECOMMENDATION_CATEGORY_LABELS,
    RECOMMENDATION_EVENT_LABELS,
    RECOMMENDATION_NEEDS,
    RECOMMENDATION_PURPOSES,
)
from app.modules.recommendations.engine import recommend_products
from app.ui.common import make_table, set_cell


def _decode_tags(value: str | None) -> str:
    if not value:
        return ""
    decoded = json.loads(value)
    if not isinstance(decoded, list) or any(not isinstance(tag, str) for tag in decoded):
        raise ValueError("Danh sách thẻ trong hồ sơ sản phẩm không hợp lệ.")
    return ", ".join(decoded)


class RecommendationProfileDialog(QDialog):
    TAG_FIELDS = (
        ("species_tags", "Loài phù hợp *", "cho, meo, tho, hamster, chim"),
        ("age_groups", "Nhóm tuổi", "baby, young, adult, senior"),
        ("breed_tags", "Giống phù hợp", "poodle, corgi, samoyed"),
        ("gender_tags", "Giới tính phù hợp", "đực, cái"),
        ("needs_tags", "Nhu cầu", "shedding, digestion, weight_control"),
        ("health_tags", "Thẻ sức khỏe phù hợp", "sensitive_skin, dental_care"),
        ("activity_tags", "Mức vận động", "low_activity, high_activity"),
        ("coat_tags", "Đặc điểm lông", "long_coat, short_coat"),
        ("environment_tags", "Môi trường", "indoor, outdoor"),
        ("avoid_tags", "Thẻ cần tránh (dị ứng)", "chicken, dairy, fragrance"),
    )

    def __init__(
        self,
        parent: QWidget,
        item: sqlite3.Row,
        profile: sqlite3.Row | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cấu hình sản phẩm gợi ý")
        self.setMinimumSize(620, 720)
        root = QVBoxLayout(self)
        root.addWidget(
            QLabel(
                f"{item['item_code']} — {item['name']}",
                objectName="sectionTitle",
            )
        )
        root.addWidget(
            QLabel(
                "Thẻ dùng chữ thường, phân tách bằng dấu phẩy. Loài/nhu cầu cần "
                "viết thống nhất giữa hồ sơ bé và sản phẩm."
            )
        )
        form = QFormLayout()
        self.category = QComboBox()
        for category in RECOMMENDATION_CATEGORIES:
            self.category.addItem(
                RECOMMENDATION_CATEGORY_LABELS[category], category
            )
        form.addRow("Nhóm gợi ý", self.category)
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1_000_000_000)
        self.price.setDecimals(0)
        self.price.setSuffix(" ₫")
        form.addRow("Giá bán tham khảo", self.price)
        self.popularity = QSpinBox()
        self.popularity.setRange(0, 100)
        form.addRow("Mức phổ biến (0–100)", self.popularity)
        self.tag_inputs: dict[str, QLineEdit] = {}
        for key, label, placeholder in self.TAG_FIELDS:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            self.tag_inputs[key] = field
            form.addRow(label, field)

        weight_group = QGroupBox("Giới hạn cân nặng (kg, nếu có)")
        weight_layout = QHBoxLayout(weight_group)
        self.weight_enabled = QCheckBox("Áp dụng khoảng cân nặng")
        self.minimum_weight = QDoubleSpinBox()
        self.minimum_weight.setRange(0, 100_000)
        self.minimum_weight.setDecimals(2)
        self.maximum_weight = QDoubleSpinBox()
        self.maximum_weight.setRange(0, 100_000)
        self.maximum_weight.setDecimals(2)
        self.minimum_weight.setEnabled(False)
        self.maximum_weight.setEnabled(False)
        self.weight_enabled.toggled.connect(self.minimum_weight.setEnabled)
        self.weight_enabled.toggled.connect(self.maximum_weight.setEnabled)
        weight_layout.addWidget(self.weight_enabled)
        weight_layout.addWidget(QLabel("Từ"))
        weight_layout.addWidget(self.minimum_weight)
        weight_layout.addWidget(QLabel("đến"))
        weight_layout.addWidget(self.maximum_weight)
        form.addRow(weight_group)
        self.note = QLineEdit()
        self.note.setPlaceholderText("Ghi chú cho nhân viên tư vấn")
        form.addRow("Ghi chú", self.note)
        root.addLayout(form)
        self.warning = QLabel()
        self.warning.setWordWrap(True)
        self.warning.setStyleSheet("color: #a33; font-weight: 600;")
        root.addWidget(self.warning)
        self.category.currentIndexChanged.connect(self._category_changed)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        if profile and profile["recommendation_category"]:
            self.category.setCurrentIndex(
                self.category.findData(profile["recommendation_category"])
            )
            self.price.setValue(profile["recommendation_price"])
            self.popularity.setValue(profile["popularity"])
            for key, field in self.tag_inputs.items():
                field.setText(_decode_tags(profile[key]))
            if (
                profile["minimum_weight"] is not None
                or profile["maximum_weight"] is not None
            ):
                self.weight_enabled.setChecked(True)
                self.minimum_weight.setValue(profile["minimum_weight"] or 0)
                self.maximum_weight.setValue(profile["maximum_weight"] or 0)
            self.note.setText(profile["note"])
        self._category_changed()

    def _category_changed(self, *_: Any) -> None:
        if self.category.currentData() == "VETERINARY":
            self.warning.setText(
                "Sản phẩm thuốc/thú y sẽ không xuất hiện trong gợi ý tự động; "
                "cần bác sĩ thú y tư vấn."
            )
        else:
            self.warning.setText(
                "Gợi ý hỗ trợ tư vấn, không thay thế chỉ định thú y. "
                "Không cấu hình sản phẩm cho loài/nhu cầu chưa được kiểm chứng."
            )

    def _validate(self) -> None:
        if (
            self.category.currentData() in {"FOOD", "SUPPLEMENT"}
            and not self.tag_inputs["species_tags"].text().strip()
        ):
            QMessageBox.warning(
                self,
                "Thiếu đối tượng phù hợp",
                "Sản phẩm ăn uống/bổ sung cần khai báo ít nhất một loài phù hợp.",
            )
            return
        if self.weight_enabled.isChecked() and (
            self.minimum_weight.value() > self.maximum_weight.value()
        ):
            QMessageBox.warning(
                self,
                "Khoảng cân nặng không hợp lệ",
                "Cân nặng tối thiểu phải nhỏ hơn hoặc bằng tối đa.",
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        values: dict[str, Any] = {
            key: field.text()
            for key, field in self.tag_inputs.items()
        }
        values.update(
            {
                "recommendation_category": self.category.currentData(),
                "recommendation_price": self.price.value(),
                "popularity": self.popularity.value(),
                "minimum_weight": (
                    self.minimum_weight.value()
                    if self.weight_enabled.isChecked()
                    else None
                ),
                "maximum_weight": (
                    self.maximum_weight.value()
                    if self.weight_enabled.isChecked()
                    else None
                ),
                "note": self.note.text().strip(),
            }
        )
        return values


class RecommendationsDialog(QDialog):
    def __init__(self, parent: QWidget, database: Database) -> None:
        super().__init__(parent)
        self.database = database
        self.results: list[dict[str, Any]] = []
        self.setWindowTitle("Gợi ý sản phẩm theo hồ sơ thú cưng")
        self.setMinimumSize(1040, 760)
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Sản phẩm phù hợp với từng bé", objectName="pageTitle"))
        root.addWidget(
            QLabel(
                "Chấm điểm minh bạch theo loài, tuổi, giống/giới tính, nhu cầu, "
                "hành vi, lịch sử mua, độ phổ biến và tồn kho "
                "(30/15/15/15/10/5/5/5%); hành vi còn dùng đồng xuất hiện "
                "ẩn danh giữa các hồ sơ thú cưng. "
                "Thuốc/thú y không nằm trong gợi ý tự động."
            )
        )
        filters = QFormLayout()
        self.animal = QComboBox()
        for animal in database.list_animals():
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']} "
                f"({animal['species']}, {animal['breed'] or 'chưa rõ giống'})",
                animal["id"],
            )
        self.customer = QComboBox()
        self.customer.addItem("Không gắn khách hàng", None)
        for customer in database.list_customers():
            self.customer.addItem(
                f"{customer['customer_code']} — {customer['name']}",
                customer["id"],
            )
        self.purpose = QComboBox()
        self.purpose.addItem("Tất cả nhu cầu", "ALL")
        for category, label in RECOMMENDATION_PURPOSES.items():
            self.purpose.addItem(label, category)
        self.budget = QComboBox()
        self.budget.addItem("Không giới hạn", None)
        for label, price_range in (
            ("Dưới 100.000 ₫", (0, 100_000)),
            ("100.000–300.000 ₫", (100_000, 300_000)),
            ("300.000–500.000 ₫", (300_000, 500_000)),
            ("500.000–1.000.000 ₫", (500_000, 1_000_000)),
            ("Trên 1.000.000 ₫", (1_000_000, None)),
        ):
            self.budget.addItem(label, price_range)
        filters.addRow("Thú cưng", self.animal)
        filters.addRow("Khách hàng (tùy chọn)", self.customer)
        filters.addRow("Mục đích mua", self.purpose)
        filters.addRow("Ngân sách", self.budget)
        root.addLayout(filters)

        needs_group = QGroupBox("Nhu cầu hiện tại (chọn nhiều mục)")
        needs_layout = QGridLayout(needs_group)
        self.needs: dict[str, QCheckBox] = {}
        for index, (key, label) in enumerate(RECOMMENDATION_NEEDS):
            checkbox = QCheckBox(label)
            self.needs[key.casefold()] = checkbox
            needs_layout.addWidget(checkbox, index // 4, index % 4)
        root.addWidget(needs_group)

        controls = QHBoxLayout()
        self.recommend_button = QPushButton(
            "✨ Phân tích và gợi ý", objectName="primaryButton"
        )
        self.recommend_button.clicked.connect(self.generate)
        controls.addWidget(self.recommend_button)
        self.status = QLabel("")
        controls.addWidget(self.status, 1)
        root.addLayout(controls)
        self.table = make_table(
            ["Sản phẩm", "Nhóm", "Phù hợp", "Giải thích", "Giá", "Tồn dùng được"]
        )
        self.table.currentCellChanged.connect(self._selection_changed)
        root.addWidget(self.table, 1)
        self.details = QLabel("Chọn bé và bấm “Phân tích và gợi ý”.")
        self.details.setWordWrap(True)
        root.addWidget(self.details)

        events = QHBoxLayout()
        self.event_buttons: list[QPushButton] = []
        for label, event in (
            ("Đã xem", "VIEW"),
            ("Ghi nhận quan tâm", "CLICK"),
            ("Thích", "LIKE"),
            ("Thêm giỏ", "ADD_TO_CART"),
            ("Ghi nhận đã mua", "PURCHASE"),
        ):
            button = QPushButton(label)
            button.setEnabled(False)
            button.clicked.connect(
                lambda _checked=False, event_type=event: self.record_event(event_type)
            )
            events.addWidget(button)
            self.event_buttons.append(button)
        root.addLayout(events)
        root.addWidget(
            QLabel(
                "Ghi nhận “Đã mua” chỉ dùng cá nhân hóa gợi ý, không tạo hóa đơn "
                "và không tự trừ tồn kho."
            )
        )
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        root.addWidget(buttons)
        if self.animal.count() == 0:
            self.recommend_button.setEnabled(False)
            self.status.setText("Cần có hồ sơ thú cưng trước khi gợi ý.")

    def _selected_item_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def generate(self, *_: Any) -> None:
        animal_id = self.animal.currentData()
        if animal_id is None:
            return
        animal = self.database.get_animal(animal_id)
        if animal is None:
            QMessageBox.warning(self, "Không tìm thấy", "Hồ sơ thú cưng không còn tồn tại.")
            self.accept()
            return
        price_range = self.budget.currentData()
        minimum_price, maximum_price = price_range or (None, None)
        selected_needs = {
            key for key, checkbox in self.needs.items() if checkbox.isChecked()
        }
        customer_id = self.customer.currentData()
        try:
            interactions = self.database.list_recommendation_interactions(
                animal_id, customer_id
            )
            collaborative_interactions = (
                self.database.list_recommendation_peer_interactions(
                    animal_id, customer_id
                )
            )
            product_preferences = self.database.list_animal_product_preferences(
                animal_id
            )
            products = [
                dict(product)
                for product in self.database.list_recommendation_products()
            ]
            self.results = recommend_products(
                products,
                dict(animal),
                interactions,
                selected_needs,
                self.purpose.currentData(),
                minimum_price,
                maximum_price,
                collaborative_interactions=collaborative_interactions,
                product_preferences=product_preferences,
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tạo gợi ý", str(error))
            return
        self.table.setRowCount(len(self.results))
        for row, product in enumerate(self.results):
            set_cell(self.table, row, 0, product["name"])
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, product["item_id"])
            set_cell(
                self.table,
                row,
                1,
                RECOMMENDATION_CATEGORY_LABELS[product["recommendation_category"]],
            )
            set_cell(self.table, row, 2, f"{product['score']:.1f}%")
            explanations = list(product["reasons"])
            graph_paths = product.get("knowledge_paths", [])
            if graph_paths:
                explanations.append(
                    "Đồ thị tri thức: "
                    + ", ".join(path["label"] for path in graph_paths)
                )
            set_cell(self.table, row, 3, " · ".join(explanations))
            set_cell(self.table, row, 4, f"{product['recommendation_price']:,.0f} ₫")
            set_cell(
                self.table,
                row,
                5,
                f"{product['usable_quantity']:g} {product['unit']}",
            )
        if self.results:
            self.table.selectRow(0)
            self.status.setText(
                f"Tìm được {len(self.results)} sản phẩm còn hàng, phù hợp."
            )
        else:
            self.details.setText(
                "Chưa có sản phẩm phù hợp còn hàng. Kiểm tra cấu hình loài, "
                "thẻ nhu cầu, ngân sách và tồn kho."
            )
            self.status.setText("Không có kết quả phù hợp.")
        self._selection_changed()

    def _selection_changed(self, *_: Any) -> None:
        item_id = self._selected_item_id()
        selected = next(
            (product for product in self.results if product["item_id"] == item_id),
            None,
        )
        for button in self.event_buttons:
            button.setEnabled(selected is not None)
        if selected is None:
            return
        breakdown = selected["score_breakdown"]
        self.details.setText(
            f"Điểm {selected['score']:.1f}% — "
            f"loài {breakdown['species']:.0f}, tuổi {breakdown['age']:.0f}, "
            f"giống/giới tính {breakdown['breed']:.0f}, nhu cầu {breakdown['needs']:.0f}, "
            f"hành vi {breakdown['behavior']:.0f}, lịch sử mua "
            f"{breakdown['purchase_history']:.0f}, phổ biến {breakdown['popularity']:.0f}, "
            f"tồn kho {breakdown['stock']:.0f}. "
            f"Ghi chú: {selected['note'] or 'không có'}."
        )

    def record_event(self, event_type: str) -> None:
        animal_id = self.animal.currentData()
        item_id = self._selected_item_id()
        if animal_id is None or item_id is None:
            return
        if event_type == "PURCHASE":
            answer = QMessageBox.question(
                self,
                "Ghi nhận hành vi mua",
                "Chỉ lưu dấu vết mua để cá nhân hóa gợi ý; không tạo hóa đơn "
                "và không trừ tồn. Bạn xác nhận?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            self.database.record_recommendation_interaction(
                animal_id,
                item_id,
                event_type,
                self.customer.currentData(),
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể ghi nhận", str(error))
            return
        self.status.setText(
            f"Đã ghi nhận: {RECOMMENDATION_EVENT_LABELS[event_type]}."
        )
        self.generate()
