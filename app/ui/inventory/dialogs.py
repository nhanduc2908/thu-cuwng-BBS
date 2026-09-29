import sqlite3
from typing import Any

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from app.modules.inventory.constants import INVENTORY_CATEGORIES, INVENTORY_CATEGORY_LABELS
from app.modules.inventory.catalog_seed import PRODUCT_GROUPS
from app.database import Database
from app.ui.common import make_table, set_cell


class InventoryItemDialog(QDialog):
    def __init__(
        self, parent: QWidget, item: sqlite3.Row | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cập nhật vật tư" if item else "Thêm vật tư")
        self.resize(560, 720)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.category = QComboBox()
        for value in INVENTORY_CATEGORIES:
            self.category.addItem(INVENTORY_CATEGORY_LABELS[value], value)
        self.catalog_category = QComboBox()
        self.catalog_category.setEditable(True)
        self.catalog_category.addItem("")
        for group in PRODUCT_GROUPS:
            self.catalog_category.addItem(group["name"])
        self.species = QLineEdit()
        self.age_group = QLineEdit()
        self.subspecies = QLineEdit()
        self.age_min_months = QLineEdit()
        self.age_max_months = QLineEdit()
        self.age_unit = QComboBox()
        self.age_unit.addItem("Tháng", "MONTH")
        self.age_unit.addItem("Năm", "YEAR")
        self.age_unit.addItem("Theo nhãn", "LABEL")
        self.life_stage = QLineEdit()
        self.food_category = QLineEdit()
        self.food_type = QLineEdit()
        self.food_subtype = QLineEdit()
        self.breed_size = QLineEdit()
        self.suitable_weight_min = QLineEdit()
        self.suitable_weight_max = QLineEdit()
        self.feeding_frequency = QLineEdit("Theo hướng dẫn sản phẩm")
        self.feeding_time = QLineEdit()
        self.serving_size = QLineEdit()
        self.protein_source = QLineEdit()
        self.nutrition_type = QLineEdit()
        self.purpose = QLineEdit()
        self.vitamin_c_content = QLineEdit()
        self.water_level = QLineEdit()
        self.diet_type = QLineEdit()
        self.pack_size = QLineEdit()
        self.brand = QLineEdit()
        self.barcode = QLineEdit()
        self.retail_price = QDoubleSpinBox()
        self.retail_price.setRange(0, 1_000_000_000)
        self.retail_price.setDecimals(0)
        self.retail_price.setSuffix(" VND")
        self.member_price_enabled = QCheckBox("Có giá hội viên riêng")
        self.member_price = QDoubleSpinBox()
        self.member_price.setRange(0, 1_000_000_000)
        self.member_price.setDecimals(0)
        self.member_price.setSuffix(" VND")
        self.member_price_enabled.toggled.connect(self.member_price.setEnabled)
        self.member_price.setEnabled(False)
        self.promotion_percent = QDoubleSpinBox()
        self.promotion_percent.setRange(0, 100)
        self.promotion_percent.setSuffix(" %")
        self.promotion_note = QLineEdit()
        self.ingredients = QLineEdit()
        self.image_path = QLineEdit()
        self.unit = QLineEdit()
        self.minimum = QDoubleSpinBox()
        self.minimum.setRange(0, 1_000_000_000)
        self.minimum.setDecimals(3)
        self.description = QTextEdit()
        self.description.setMaximumHeight(75)
        for label, widget in (
            ("Mã vật tư *", self.code),
            ("Tên *", self.name),
            ("Nhóm tồn kho", self.category),
            ("Danh mục sản phẩm", self.catalog_category),
            ("Loài phù hợp", self.species),
            ("Phân loài", self.subspecies),
            ("Độ tuổi", self.age_group),
            ("Tuổi bắt đầu (theo đơn vị đã chọn)", self.age_min_months),
            ("Tuổi kết thúc (theo đơn vị đã chọn)", self.age_max_months),
            ("Đơn vị tuổi", self.age_unit),
            ("Giai đoạn sống", self.life_stage),
            ("Nhóm thức ăn", self.food_category),
            ("Loại thức ăn", self.food_type),
            ("Phân loại thức ăn", self.food_subtype),
            ("Kích thước giống", self.breed_size),
            ("Cân nặng phù hợp tối thiểu (kg)", self.suitable_weight_min),
            ("Cân nặng phù hợp tối đa (kg)", self.suitable_weight_max),
            ("Tần suất", self.feeding_frequency),
            ("Thời điểm cho ăn", self.feeding_time),
            ("Khẩu phần (theo nhãn)", self.serving_size),
            ("Nguồn protein", self.protein_source),
            ("Loại dinh dưỡng", self.nutrition_type),
            ("Mục đích", self.purpose),
            ("Vitamin C (theo nhãn)", self.vitamin_c_content),
            ("Tầng nước", self.water_level),
            ("Kiểu ăn", self.diet_type),
            ("Quy cách", self.pack_size),
            ("Thương hiệu", self.brand),
            ("Barcode", self.barcode),
            ("Giá bán đề xuất", self.retail_price),
            ("Giá thành viên", self.member_price_enabled),
            ("", self.member_price),
            ("Khuyến mãi", self.promotion_percent),
            ("Ghi chú khuyến mãi", self.promotion_note),
            ("Thành phần", self.ingredients),
            ("Đường dẫn ảnh", self.image_path),
            ("Đơn vị tính *", self.unit),
            ("Ngưỡng tồn tối thiểu", self.minimum),
            ("Mô tả", self.description),
        ):
            form.addRow(label, widget)
        form_content = QWidget()
        form_content.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_content)
        layout.addWidget(scroll, 1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if item:
            self.code.setText(item["item_code"])
            self.name.setText(item["name"])
            self.category.setCurrentIndex(self.category.findData(item["category"]))
            self.catalog_category.setCurrentText(item["catalog_category"])
            self.species.setText(item["target_species"])
            self.age_group.setText(item["age_group"])
            self.subspecies.setText(item["animal_subspecies"])
            self.age_min_months.setText(
                "" if item["age_min_months"] is None else str(item["age_min_months"])
            )
            self.age_max_months.setText(
                "" if item["age_max_months"] is None else str(item["age_max_months"])
            )
            self.age_unit.setCurrentIndex(self.age_unit.findData(item["age_unit"]))
            self.life_stage.setText(item["life_stage"])
            self.food_category.setText(item["food_category"])
            self.food_type.setText(item["food_type"])
            self.food_subtype.setText(item["food_subtype"])
            self.breed_size.setText(item["breed_size"])
            self.suitable_weight_min.setText(
                "" if item["suitable_weight_min"] is None else str(item["suitable_weight_min"])
            )
            self.suitable_weight_max.setText(
                "" if item["suitable_weight_max"] is None else str(item["suitable_weight_max"])
            )
            self.feeding_frequency.setText(item["feeding_frequency"])
            self.feeding_time.setText(item["feeding_time"])
            self.serving_size.setText(item["serving_size"])
            self.protein_source.setText(item["protein_source"])
            self.nutrition_type.setText(item["nutrition_type"])
            self.purpose.setText(item["purpose"])
            self.vitamin_c_content.setText(item["vitamin_c_content"])
            self.water_level.setText(item["water_level"])
            self.diet_type.setText(item["diet_type"])
            self.pack_size.setText(item["pack_size"])
            self.brand.setText(item["brand"])
            self.barcode.setText(item["barcode"])
            self.retail_price.setValue(item["retail_price"])
            has_member_price = item["member_price"] is not None
            self.member_price_enabled.setChecked(has_member_price)
            self.member_price.setEnabled(has_member_price)
            if has_member_price:
                self.member_price.setValue(item["member_price"])
            self.promotion_percent.setValue(item["promotion_percent"])
            self.promotion_note.setText(item["promotion_note"])
            self.ingredients.setText(item["ingredients"])
            self.image_path.setText(item["image_path"])
            self.unit.setText(item["unit"])
            self.minimum.setValue(item["minimum_stock"])
            self.description.setPlainText(item["description"])

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(
                self, "Thiếu thông tin", "Mã vật tư và tên là bắt buộc."
            )
            return
        if not self.unit.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Đơn vị tính là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "item_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "category": self.category.currentData(),
            "catalog_category": self.catalog_category.currentText().strip(),
            "target_species": self.species.text().strip(),
            "age_group": self.age_group.text().strip(),
            "animal_subspecies": self.subspecies.text().strip(),
            "age_min_months": self.age_min_months.text().strip() or None,
            "age_max_months": self.age_max_months.text().strip() or None,
            "age_unit": self.age_unit.currentData(),
            "life_stage": self.life_stage.text().strip(),
            "food_category": self.food_category.text().strip(),
            "food_type": self.food_type.text().strip(),
            "food_subtype": self.food_subtype.text().strip(),
            "breed_size": self.breed_size.text().strip(),
            "suitable_weight_min": self.suitable_weight_min.text().strip() or None,
            "suitable_weight_max": self.suitable_weight_max.text().strip() or None,
            "feeding_frequency": self.feeding_frequency.text().strip(),
            "feeding_time": self.feeding_time.text().strip(),
            "serving_size": self.serving_size.text().strip(),
            "protein_source": self.protein_source.text().strip(),
            "nutrition_type": self.nutrition_type.text().strip(),
            "purpose": self.purpose.text().strip(),
            "vitamin_c_content": self.vitamin_c_content.text().strip(),
            "water_level": self.water_level.text().strip(),
            "diet_type": self.diet_type.text().strip(),
            "pack_size": self.pack_size.text().strip(),
            "brand": self.brand.text().strip(),
            "barcode": self.barcode.text().strip(),
            "retail_price": self.retail_price.value(),
            "member_price": (
                self.member_price.value() if self.member_price_enabled.isChecked() else None
            ),
            "promotion_percent": self.promotion_percent.value(),
            "promotion_note": self.promotion_note.text().strip(),
            "ingredients": self.ingredients.text().strip(),
            "image_path": self.image_path.text().strip(),
            "unit": self.unit.text().strip(),
            "minimum_stock": self.minimum.value(),
            "description": self.description.toPlainText().strip(),
        }


class FeedingAgeRuleEditorDialog(QDialog):
    def __init__(self, parent: QWidget, rule: sqlite3.Row | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Sửa quy tắc tuổi" if rule else "Thêm quy tắc tuổi")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.species = QLineEdit()
        self.subspecies = QLineEdit()
        self.size = QLineEdit("ALL")
        self.stage = QLineEdit()
        self.minimum = QLineEdit()
        self.maximum = QLineEdit()
        self.unit = QComboBox()
        for label, value in (
            ("Tháng", "MONTH"),
            ("Năm", "YEAR"),
            ("Theo loài cụ thể", "SPECIES"),
            ("Theo nhãn sản phẩm", "LABEL"),
        ):
            self.unit.addItem(label, value)
        self.food_category = QLineEdit()
        self.food_type = QLineEdit()
        self.active = QCheckBox("Đang áp dụng")
        self.active.setChecked(True)
        self.note = QLineEdit()
        for label, widget in (
            ("Mã quy tắc *", self.code),
            ("Loài *", self.species),
            ("Phân loài", self.subspecies),
            ("Kích thước giống", self.size),
            ("Giai đoạn sống *", self.stage),
            ("Tuổi bắt đầu (theo đơn vị đã chọn)", self.minimum),
            ("Tuổi kết thúc (theo đơn vị đã chọn)", self.maximum),
            ("Đơn vị/mức tin cậy", self.unit),
            ("Nhóm thức ăn", self.food_category),
            ("Loại thức ăn", self.food_type),
            ("Trạng thái", self.active),
            ("Ghi chú", self.note),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if rule:
            self.code.setText(rule["code"])
            self.species.setText(rule["species"])
            self.subspecies.setText(rule["subspecies"])
            self.size.setText(rule["breed_size"])
            self.stage.setText(rule["life_stage"])
            self.minimum.setText(
                "" if rule["age_min_months"] is None else str(rule["age_min_months"])
            )
            self.maximum.setText(
                "" if rule["age_max_months"] is None else str(rule["age_max_months"])
            )
            unit_index = self.unit.findData(rule["age_unit"])
            if unit_index >= 0:
                self.unit.setCurrentIndex(unit_index)
            self.food_category.setText(rule["food_category"])
            self.food_type.setText(rule["food_type"])
            self.active.setChecked(rule["status"] == "ACTIVE")
            self.note.setText(rule["note"])

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.species.text().strip() or not self.stage.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã, loài và giai đoạn là bắt buộc.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "code": self.code.text(),
            "species": self.species.text(),
            "subspecies": self.subspecies.text(),
            "breed_size": self.size.text(),
            "life_stage": self.stage.text(),
            "age_min_months": self.minimum.text().strip() or None,
            "age_max_months": self.maximum.text().strip() or None,
            "age_unit": self.unit.currentData(),
            "food_category": self.food_category.text(),
            "food_type": self.food_type.text(),
            "is_active": self.active.isChecked(),
            "note": self.note.text(),
        }


class FeedingAgeRulesDialog(QDialog):
    def __init__(self, parent: QWidget, database: Database) -> None:
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Quy tắc độ tuổi thức ăn")
        self.resize(980, 560)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Các mốc mẫu dùng để phân loại catalog; loài ngoại lai, chim và cá "
                "cần quy tắc theo loài/nhãn, không suy ra khẩu phần."
            )
        )
        self.table = make_table(
            ["Mã", "Loài", "Phân loài", "Kích thước", "Giai đoạn",
             "Từ tuổi", "Đến tuổi", "Đơn vị", "Thức ăn", "Trạng thái"]
        )
        layout.addWidget(self.table, 1)
        buttons = QHBoxLayout()
        self.add_button = QPushButton("＋ Thêm")
        self.edit_button = QPushButton("Sửa")
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.add_button.clicked.connect(self.add_rule)
        self.edit_button.clicked.connect(self.edit_rule)
        close.rejected.connect(self.reject)
        close.accepted.connect(self.accept)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.edit_button)
        buttons.addStretch()
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self) -> None:
        rules = self.database.list_feeding_age_rules(active_only=False)
        self.table.setRowCount(len(rules))
        for row, rule in enumerate(rules):
            values = (
                rule["code"],
                rule["species"],
                rule["subspecies"] or "Tất cả",
                rule["breed_size"],
                rule["life_stage"],
                rule["age_min_months"] if rule["age_min_months"] is not None else "—",
                rule["age_max_months"] if rule["age_max_months"] is not None else "—",
                rule["age_unit"],
                rule["food_type"] or rule["food_category"] or "—",
                "Đang áp dụng" if rule["status"] == "ACTIVE" else "Ngừng",
            )
            for column, value in enumerate(values):
                set_cell(self.table, row, column, value)
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, rule["id"])

    def add_rule(self) -> None:
        self._edit()

    def edit_rule(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Chọn quy tắc", "Hãy chọn quy tắc cần sửa.")
            return
        rule_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        rule = next(
            (item for item in self.database.list_feeding_age_rules(False)
             if item["id"] == rule_id),
            None,
        )
        if rule is None:
            QMessageBox.warning(self, "Không tìm thấy", "Quy tắc không còn tồn tại.")
            return
        self._edit(int(rule_id), rule)

    def _edit(self, rule_id: int | None = None, rule: sqlite3.Row | None = None) -> None:
        dialog = FeedingAgeRuleEditorDialog(self, rule)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.save_feeding_age_rule(dialog.values(), rule_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lưu quy tắc", str(error))
            return
        self.refresh()


class FeedingRecommendationsDialog(QDialog):
    def __init__(
        self, parent: QWidget, animal: sqlite3.Row, results: dict[str, Any]
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Thức ăn phù hợp — {animal['name']}")
        self.resize(920, 540)
        layout = QVBoxLayout(self)
        stages = ", ".join(results["life_stages"]) or "chưa xác định"
        age = (
            f"{results['age_months']} tháng"
            if results["age_months"] is not None
            else "chưa rõ tuổi"
        )
        layout.addWidget(
            QLabel(f"{animal['species']} · {animal['breed'] or 'chưa rõ giống'} · {age} · {stages}")
        )
        warning = QLabel(results["notice"])
        warning.setWordWrap(True)
        layout.addWidget(warning)
        self.table = make_table(
            ["Mã", "Sản phẩm", "Loài", "Giai đoạn", "Loại thức ăn",
             "Protein", "Khẩu phần/tần suất", "Giá", "Tồn"]
        )
        products = results["products"]
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            values = (
                product["item_code"],
                product["name"],
                product["target_species"],
                product["life_stage"] or product["age_group"] or "Theo nhãn",
                " / ".join(
                    value for value in (product["food_category"], product["food_type"], product["food_subtype"])
                    if value
                ) or product["catalog_category"],
                product["protein_source"] or "Theo nhãn",
                " · ".join(
                    value
                    for value in (
                        product["serving_size"],
                        product["feeding_frequency"],
                    )
                    if value
                ),
                f"{product['retail_price']:,.0f} VND",
                f"{product['usable_quantity']:g} {product['unit']}",
            )
            for column, value in enumerate(values):
                set_cell(self.table, row, column, value)
        layout.addWidget(self.table, 1)
        if not products:
            layout.addWidget(QLabel("Chưa có sản phẩm thức ăn đã khai báo metadata phù hợp và còn tồn."))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class ProductComboEditorDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        products: list[sqlite3.Row],
        combo: sqlite3.Row | None = None,
        components: list[sqlite3.Row] | None = None,
    ) -> None:
        super().__init__(parent)
        self.products = products
        self.component_quantities = {
            int(component["item_id"]): float(component["quantity"])
            for component in (components or [])
        }
        self.product_rows: list[sqlite3.Row] = []
        self.setWindowTitle("Sửa combo" if combo else "Tạo combo")
        self.resize(1050, 720)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.species = QLineEdit()
        self.description = QLineEdit()
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1_000_000_000)
        self.price.setDecimals(0)
        self.member_price_enabled = QCheckBox("Có giá hội viên riêng")
        self.member_price = QDoubleSpinBox()
        self.member_price.setRange(0, 1_000_000_000)
        self.member_price.setDecimals(0)
        self.member_price_enabled.toggled.connect(self.member_price.setEnabled)
        self.member_price.setEnabled(False)
        self.promotion = QDoubleSpinBox()
        self.promotion.setRange(0, 100)
        self.promotion.setSuffix(" %")
        self.active = QCheckBox("Đang bán")
        self.active.setChecked(True)
        for label, widget in (
            ("Mã combo *", self.code),
            ("Tên combo *", self.name),
            ("Loài phù hợp", self.species),
            ("Mô tả", self.description),
            ("Giá combo", self.price),
            ("Giá hội viên", self.member_price_enabled),
            ("", self.member_price),
            ("Khuyến mãi", self.promotion),
            ("Trạng thái", self.active),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)

        layout.addWidget(
            QLabel("Chọn SKU thành phần và số lượng. Chỉ được bán combo khi đủ tồn từng SKU.")
        )
        self.search = QLineEdit()
        self.search.setPlaceholderText("Lọc SKU theo mã, tên hoặc danh mục")
        self.search.textChanged.connect(self._refresh_products)
        layout.addWidget(self.search)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Chọn", "SKU", "Sản phẩm", "Danh mục", "Tồn dùng được", "SL combo"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        layout.addWidget(self.table, 1)
        self._refresh_products()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if combo:
            self.code.setText(combo["combo_code"])
            self.name.setText(combo["name"])
            self.species.setText(combo["target_species"])
            self.description.setText(combo["description"])
            self.price.setValue(combo["sale_price"])
            has_member_price = combo["member_price"] is not None
            self.member_price_enabled.setChecked(has_member_price)
            self.member_price.setEnabled(has_member_price)
            if has_member_price:
                self.member_price.setValue(combo["member_price"])
            self.promotion.setValue(combo["promotion_percent"])
            self.active.setChecked(bool(combo["is_active"]))
            self.setWindowTitle(f"Sửa combo · {combo['name']}")

    def _refresh_products(self, *_: Any) -> None:
        if hasattr(self, "table"):
            selected: dict[int, float] = {}
            for row in range(self.table.rowCount()):
                check = self.table.item(row, 0)
                if check is None:
                    continue
                item_id = int(check.data(Qt.ItemDataRole.UserRole))
                if check.checkState() == Qt.CheckState.Checked:
                    selected[item_id] = self.table.cellWidget(row, 5).value()
                else:
                    self.component_quantities.pop(item_id, None)
            self.component_quantities.update(selected)
        search = self.search.text().strip().casefold()
        rows = [
            product
            for product in self.products
            if not search
            or search in str(product["item_code"]).casefold()
            or search in str(product["name"]).casefold()
            or search in str(product["catalog_category"]).casefold()
        ]
        self.product_rows = rows
        self.table.setRowCount(len(rows))
        for row, product in enumerate(rows):
            item = QTableWidgetItem()
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(
                Qt.CheckState.Checked
                if int(product["id"]) in self.component_quantities
                else Qt.CheckState.Unchecked
            )
            self.table.setItem(row, 0, item)
            for column, value in enumerate(
                (
                    product["item_code"],
                    product["name"],
                    product["catalog_category"] or product["category"],
                    f"{product['usable_quantity']:g} {product['unit']}",
                ),
                start=1,
            ):
                set_cell(self.table, row, column, value)
            quantity = QDoubleSpinBox()
            quantity.setRange(0.001, 100_000)
            quantity.setDecimals(3)
            quantity.setValue(
                self.component_quantities.get(int(product["id"]), 1)
            )
            self.table.setCellWidget(row, 5, quantity)
            self.table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, int(product["id"])
            )

    def _validate(self) -> None:
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã và tên combo là bắt buộc.")
            return
        if not self.components():
            QMessageBox.warning(self, "Thiếu thành phần", "Hãy chọn ít nhất một SKU.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "combo_code": self.code.text().strip(),
            "name": self.name.text().strip(),
            "target_species": self.species.text().strip(),
            "description": self.description.text().strip(),
            "sale_price": self.price.value(),
            "member_price": (
                self.member_price.value()
                if self.member_price_enabled.isChecked()
                else None
            ),
            "promotion_percent": self.promotion.value(),
            "is_active": self.active.isChecked(),
            "is_demo": False,
        }

    def components(self) -> list[dict[str, Any]]:
        selected: dict[int, float] = {}
        for row in range(self.table.rowCount()):
            check = self.table.item(row, 0)
            if check is None or check.checkState() != Qt.CheckState.Checked:
                continue
            item_id = int(check.data(Qt.ItemDataRole.UserRole))
            selected[item_id] = self.table.cellWidget(row, 5).value()
        for item_id, quantity in self.component_quantities.items():
            if item_id not in selected:
                continue
            # Preserve the edited quantity across catalog filtering.
            visible = next(
                (
                    row
                    for row, product in enumerate(self.product_rows)
                    if int(product["id"]) == item_id
                ),
                None,
            )
            if visible is None:
                selected[item_id] = quantity
        return [
            {"item_id": item_id, "quantity": quantity}
            for item_id, quantity in selected.items()
        ]


class ProductComboManagementDialog(QDialog):
    def __init__(self, parent: QWidget, database: Any) -> None:
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Quản lý combo sản phẩm")
        self.resize(780, 480)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Combo demo đã có thành phần mẫu; hãy kiểm tra SKU và tồn trước khi bán.")
        )
        self.table = make_table(
            ["Mã combo", "Tên combo", "Thành phần", "Giá", "Loài", "Trạng thái"]
        )
        self.table.currentCellChanged.connect(self._selection_changed)
        layout.addWidget(self.table, 1)
        actions = QHBoxLayout()
        self.create_button = QPushButton("+ Tạo combo")
        self.create_button.clicked.connect(self.create_combo)
        self.edit_button = QPushButton("Sửa combo")
        self.edit_button.clicked.connect(self.edit_combo)
        actions.addWidget(self.create_button)
        actions.addWidget(self.edit_button)
        actions.addStretch()
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        close.accepted.connect(self.accept)
        actions.addWidget(close)
        layout.addLayout(actions)
        self.refresh()

    def _selection_changed(self, *_: Any) -> None:
        self.edit_button.setEnabled(self.table.currentRow() >= 0)

    def refresh(self) -> None:
        combos = self.database.list_inventory_combos()
        self.table.setRowCount(len(combos))
        for row, combo in enumerate(combos):
            values = (
                combo["combo_code"],
                combo["name"],
                combo["component_count"],
                f"{combo['sale_price']:,.0f} VND",
                combo["target_species"],
                "Đang bán" if combo["is_active"] else "Ngừng",
            )
            for column, value in enumerate(values):
                set_cell(self.table, row, column, value)
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, combo["id"])

    def create_combo(self) -> None:
        self._edit()

    def edit_combo(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        combo_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        combo = next(
            (combo for combo in self.database.list_inventory_combos() if combo["id"] == combo_id),
            None,
        )
        if combo is None:
            QMessageBox.warning(self, "Không tìm thấy", "Combo không còn tồn tại.")
            return
        self._edit(combo_id, combo)

    def _edit(self, combo_id: int | None = None, combo: Any = None) -> None:
        products = self.database.list_inventory_items()
        components = (
            self.database.list_inventory_combo_items(combo_id)
            if combo_id is not None
            else []
        )
        editor = ProductComboEditorDialog(self, products, combo, components)
        if not editor.exec():
            return
        try:
            self.database.save_inventory_combo(
                editor.values(), editor.components(), combo_id
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lưu combo", str(error))
            return
        self.refresh()


class ReceiveStockDialog(QDialog):
    def __init__(self, parent: QWidget, unit: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nhập kho theo lô")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.batch_code = QLineEdit()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.001, 1_000_000_000)
        self.quantity.setDecimals(3)
        self.quantity.setSuffix(f" {unit}")
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setRange(0, 1_000_000_000)
        self.unit_cost.setDecimals(2)
        self.unit_cost.setSuffix(" ₫")
        self.expiry_enabled = QCheckBox("Có hạn sử dụng")
        self.expiry_date = QDateEdit(QDate.currentDate().addYears(1))
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("dd/MM/yyyy")
        self.expiry_enabled.toggled.connect(self.expiry_date.setEnabled)
        self.expiry_date.setEnabled(False)
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Mã lô *", self.batch_code)
        form.addRow("Số lượng *", self.quantity)
        form.addRow("Giá nhập / đơn vị", self.unit_cost)
        form.addRow(self.expiry_enabled)
        form.addRow("Hạn sử dụng", self.expiry_date)
        form.addRow("Mã chứng từ", self.reference)
        form.addRow("Ghi chú", self.note)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        if not self.batch_code.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Mã lô là bắt buộc.")
            return
        if (
            self.expiry_enabled.isChecked()
            and self.expiry_date.date() < QDate.currentDate()
        ):
            QMessageBox.warning(
                self, "Hạn sử dụng không hợp lệ", "Không thể nhập lô đã hết hạn."
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "batch_code": self.batch_code.text().strip(),
            "quantity": self.quantity.value(),
            "unit_cost": self.unit_cost.value(),
            "expiry_date": (
                self.expiry_date.date().toString("yyyy-MM-dd")
                if self.expiry_enabled.isChecked()
                else None
            ),
            "occurred_on": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }


class ConsumeStockDialog(QDialog):
    def __init__(
        self, parent: QWidget, unit: str, animals: list[sqlite3.Row]
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Xuất kho sử dụng")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.001, 1_000_000_000)
        self.quantity.setDecimals(3)
        self.quantity.setSuffix(f" {unit}")
        self.animal = QComboBox()
        self.animal.addItem("Không gắn với cá thể", None)
        for animal in animals:
            self.animal.addItem(
                f"{animal['animal_code']} — {animal['name']}", animal["id"]
            )
        self.reference = QLineEdit()
        self.note = QLineEdit()
        form.addRow("Số lượng *", self.quantity)
        form.addRow("Động vật (nếu có)", self.animal)
        form.addRow("Mã phiếu", self.reference)
        form.addRow("Ghi chú", self.note)
        layout.addWidget(
            QLabel("Xuất theo lô hết hạn gần nhất; không thể xuất lô đã hết hạn.")
        )
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "quantity": self.quantity.value(),
            "animal_id": self.animal.currentData(),
            "occurred_on": QDate.currentDate().toString("yyyy-MM-dd"),
            "reference": self.reference.text().strip(),
            "note": self.note.text().strip(),
        }
