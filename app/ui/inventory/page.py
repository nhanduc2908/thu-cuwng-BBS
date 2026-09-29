import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QInputDialog,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.inventory.constants import (
    INVENTORY_CATEGORY_LABELS,
    INVENTORY_MOVEMENT_LABELS,
)
from app.ui.common import make_table, set_cell
from app.ui.inventory.dialogs import (
    ConsumeStockDialog,
    InventoryItemDialog,
    FeedingAgeRulesDialog,
    FeedingRecommendationsDialog,
    ProductComboManagementDialog,
    ReceiveStockDialog,
)
from app.ui.inventory.recommendations_dialogs import (
    RecommendationProfileDialog,
    RecommendationsDialog,
)
from app.ui.inventory.advisor_dialog import PetAdvisorDialog
from app.ui.inventory.evaluation_dialog import RecommendationEvaluationDialog


class InventoryPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.manage_enabled = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Thức ăn và thuốc", objectName="pageTitle"))
        self.alert_label = QLabel()
        self.alert_label.setWordWrap(True)
        layout.addWidget(self.alert_label)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm mã hoặc tên vật tư")
        self.search.textChanged.connect(self.refresh_items)
        toolbar.addWidget(self.search, 1)
        self.add_button = QPushButton("+ Thêm vật tư", objectName="primaryButton")
        self.add_button.clicked.connect(self.add_item)
        self.edit_button = QPushButton("Sửa thông tin")
        self.edit_button.clicked.connect(self.edit_item)
        self.receive_button = QPushButton("Nhập theo lô")
        self.receive_button.clicked.connect(self.receive_stock)
        self.consume_button = QPushButton("Xuất sử dụng")
        self.consume_button.clicked.connect(self.consume_stock)
        self.active_button = QPushButton("Ngừng hoạt động")
        self.active_button.clicked.connect(self.toggle_active)
        self.combos_button = QPushButton("Quản lý combo")
        self.combos_button.clicked.connect(self.manage_combos)
        self.feeding_rules_button = QPushButton("Quy tắc độ tuổi thức ăn")
        self.feeding_rules_button.clicked.connect(self.manage_feeding_rules)
        self.feeding_recommend_button = QPushButton(
            "🍽 Gợi ý thức ăn theo tuổi"
        )
        self.feeding_recommend_button.clicked.connect(
            self.open_feeding_recommendations
        )
        for button in (
            self.add_button,
            self.edit_button,
            self.receive_button,
            self.consume_button,
            self.active_button,
            self.combos_button,
            self.feeding_rules_button,
            self.feeding_recommend_button,
        ):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        recommendation_toolbar = QHBoxLayout()
        recommendation_toolbar.addWidget(
            QLabel(
                "🐾 Cá nhân hóa gợi ý theo loài, tuổi, nhu cầu và tồn kho"
            )
        )
        recommendation_toolbar.addStretch()
        self.configure_recommendation_button = QPushButton("Cấu hình sản phẩm gợi ý")
        self.configure_recommendation_button.clicked.connect(
            self.configure_recommendation_profile
        )
        self.remove_recommendation_button = QPushButton("Gỡ cấu hình gợi ý")
        self.remove_recommendation_button.clicked.connect(
            self.remove_recommendation_profile
        )
        self.recommend_button = QPushButton(
            "✨ Gợi ý theo hồ sơ bé", objectName="primaryButton"
        )
        self.recommend_button.clicked.connect(self.open_recommendations)
        self.advisor_button = QPushButton("🤖 AI PetCare Advisor")
        self.advisor_button.clicked.connect(self.open_advisor)
        self.evaluation_button = QPushButton("📊 Đánh giá AI")
        self.evaluation_button.clicked.connect(self.open_recommendation_evaluation)
        recommendation_toolbar.addWidget(self.configure_recommendation_button)
        recommendation_toolbar.addWidget(self.remove_recommendation_button)
        recommendation_toolbar.addWidget(self.recommend_button)
        recommendation_toolbar.addWidget(self.advisor_button)
        recommendation_toolbar.addWidget(self.evaluation_button)
        layout.addLayout(recommendation_toolbar)

        self.items_table = make_table(
            [
                "Mã",
                "Sản phẩm",
                "Danh mục",
                "Giá bán",
                "Giá hội viên",
                "Tồn dùng được",
                "Tổng tồn",
                "Tối thiểu",
                "Hết hạn",
                "Đơn vị",
                "Trạng thái",
            ]
        )
        self.items_table.currentCellChanged.connect(self._selection_changed)
        layout.addWidget(self.items_table, 3)
        self.batches_table = make_table(
            ["Mã lô", "Hạn sử dụng", "Còn lại", "Giá nhập/đv"]
        )
        layout.addWidget(QLabel("Tồn theo lô", objectName="sectionTitle"))
        layout.addWidget(self.batches_table, 1)
        self.movements_table = make_table(
            ["Ngày", "Loại", "Mã lô", "Số lượng", "Động vật", "Chứng từ", "Ghi chú"]
        )
        layout.addWidget(QLabel("Sổ nhập/xuất", objectName="sectionTitle"))
        layout.addWidget(self.movements_table, 2)
        self.refresh_items()

    def set_manage_enabled(self, enabled: bool) -> None:
        self.manage_enabled = enabled
        for button in (
            self.add_button,
            self.edit_button,
            self.receive_button,
            self.consume_button,
            self.active_button,
            self.combos_button,
            self.feeding_rules_button,
        ):
            button.setVisible(enabled)
        self.configure_recommendation_button.setVisible(enabled)
        self.remove_recommendation_button.setVisible(enabled)

    def selected_item_id(self) -> int | None:
        row = self.items_table.currentRow()
        if row < 0 or self.items_table.item(row, 0) is None:
            return None
        return self.items_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def refresh(self, *_: Any) -> None:
        self.refresh_items()

    def refresh_items(self, *_: Any) -> None:
        selected_id = self.selected_item_id()
        items = self.database.list_inventory_items(self.search.text())
        self.items_table.setRowCount(len(items))
        selected_row = -1
        for row, item in enumerate(items):
            set_cell(self.items_table, row, 0, item["item_code"])
            self.items_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, item["id"]
            )
            if item["id"] == selected_id:
                selected_row = row
            display_name = item["name"]
            if item["pack_size"]:
                display_name += f" · {item['pack_size']}"
            set_cell(self.items_table, row, 1, display_name)
            set_cell(
                self.items_table,
                row,
                2,
                item["catalog_category"]
                or INVENTORY_CATEGORY_LABELS[item["category"]],
            )
            set_cell(
                self.items_table,
                row,
                3,
                f"{item['retail_price']:,.0f} ₫" if item["retail_price"] else "—",
            )
            set_cell(
                self.items_table,
                row,
                4,
                f"{item['member_price']:,.0f} ₫"
                if item["member_price"] is not None
                else "Theo hạng",
            )
            set_cell(
                self.items_table,
                row,
                5,
                f"{item['usable_quantity']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                6,
                f"{item['stock_quantity']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                7,
                f"{item['minimum_stock']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                8,
                f"{item['expired_quantity']:g} {item['unit']}",
            )
            set_cell(self.items_table, row, 9, item["unit"])
            set_cell(
                self.items_table,
                row,
                10,
                "Đang dùng" if item["is_active"] else "Ngừng",
            )
        if selected_row >= 0:
            self.items_table.selectRow(selected_row)
        elif items:
            self.items_table.selectRow(0)
        self._selection_changed()
        self._refresh_alerts()

    def _refresh_alerts(self) -> None:
        low_items = self.database.low_stock_items()
        expiring = self.database.expiring_inventory_batches(30)
        self.alert_label.setText(
            f"Cảnh báo: {len(low_items)} vật tư ở dưới ngưỡng tồn; "
            f"{len(expiring)} lô hết hạn hoặc sẽ hết hạn trong 30 ngày."
        )
        self.alert_label.setStyleSheet(
            "color: #a33; font-weight: 600;"
            if low_items or expiring
            else "color: #287b68;"
        )

    def _selection_changed(self, *_: Any) -> None:
        item_id = self.selected_item_id()
        item = self.database.get_inventory_item(item_id) if item_id is not None else None
        self.edit_button.setEnabled(self.manage_enabled and item is not None)
        self.receive_button.setEnabled(
            self.manage_enabled and item is not None and bool(item["is_active"])
        )
        self.consume_button.setEnabled(
            self.manage_enabled
            and item is not None
            and bool(item["is_active"])
            and item["usable_quantity"] > 0
        )
        self.active_button.setEnabled(self.manage_enabled and item is not None)
        self.active_button.setText(
            "Kích hoạt lại"
            if item is not None and not item["is_active"]
            else "Ngừng hoạt động"
        )
        profile = (
            self.database.get_recommendation_profile(item_id)
            if item_id is not None
            else None
        )
        self.configure_recommendation_button.setEnabled(
            self.manage_enabled and item is not None
        )
        self.remove_recommendation_button.setEnabled(
            self.manage_enabled
            and profile is not None
            and profile["recommendation_category"] is not None
        )
        self.batches_table.setRowCount(0)
        self.movements_table.setRowCount(0)
        if item_id is None:
            return
        batches = self.database.list_inventory_batches(item_id)
        self.batches_table.setRowCount(len(batches))
        for row, batch in enumerate(batches):
            set_cell(self.batches_table, row, 0, batch["batch_code"])
            set_cell(
                self.batches_table,
                row,
                1,
                batch["expiry_date"] or "Không có hạn",
            )
            set_cell(
                self.batches_table,
                row,
                2,
                f"{batch['quantity_remaining']:g} {item['unit']}",
            )
            set_cell(
                self.batches_table, row, 3, f"{batch['unit_cost']:,.0f} ₫"
            )
        movements = self.database.list_inventory_movements(item_id)
        self.movements_table.setRowCount(len(movements))
        for row, movement in enumerate(movements):
            set_cell(self.movements_table, row, 0, movement["occurred_on"])
            set_cell(
                self.movements_table,
                row,
                1,
                INVENTORY_MOVEMENT_LABELS.get(
                    movement["movement_type"], movement["movement_type"]
                ),
            )
            set_cell(self.movements_table, row, 2, movement["batch_code"])
            set_cell(
                self.movements_table,
                row,
                3,
                f"{movement['quantity']:g} {item['unit']}",
            )
            animal = movement["animal_code"] or ""
            if movement["animal_name"]:
                animal += f" — {movement['animal_name']}"
            set_cell(self.movements_table, row, 4, animal)
            set_cell(self.movements_table, row, 5, movement["reference"])
            set_cell(self.movements_table, row, 6, movement["note"])

    def manage_combos(self) -> None:
        dialog = ProductComboManagementDialog(self, self.database)
        dialog.exec()

    def manage_feeding_rules(self) -> None:
        dialog = FeedingAgeRulesDialog(self, self.database)
        dialog.exec()

    def open_feeding_recommendations(self) -> None:
        try:
            animals = self.database.list_animals()
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tải hồ sơ", str(error))
            return
        if not animals:
            QMessageBox.information(
                self,
                "Chưa có hồ sơ",
                "Hãy tạo hồ sơ động vật trước khi lọc thức ăn theo tuổi.",
            )
            return
        labels = [
            f"{animal['animal_code']} · {animal['name']} · "
            f"{animal['species']} · {animal['breed'] or 'chưa rõ giống'}"
            for animal in animals
        ]
        selected, accepted = QInputDialog.getItem(
            self, "Gợi ý thức ăn", "Chọn hồ sơ thú cưng", labels, 0, False
        )
        if not accepted:
            return
        animal = animals[labels.index(selected)]
        water_level = ""
        diet_type = ""
        species = animal["species"].casefold()
        if "cá" in species or "fish" in species:
            water_level, accepted = QInputDialog.getItem(
                self,
                "Phân loại cá",
                "Tầng nước (nếu biết)",
                ["Không lọc", "Mặt nước", "Tầng giữa", "Đáy"],
                0,
                False,
            )
            if not accepted:
                return
            water_level = "" if water_level == "Không lọc" else water_level
            diet_type, accepted = QInputDialog.getItem(
                self,
                "Phân loại cá",
                "Kiểu ăn (nếu biết)",
                ["Không lọc", "Ăn thực vật", "Ăn tạp", "Ăn thịt"],
                0,
                False,
            )
            if not accepted:
                return
            diet_type = "" if diet_type == "Không lọc" else diet_type
        try:
            results = self.database.get_feeding_recommendations(
                animal["id"], water_level, diet_type
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lọc thức ăn", str(error))
            return
        FeedingRecommendationsDialog(self, animal, results).exec()
        self.refresh_items()

    def configure_recommendation_profile(self) -> None:
        item_id = self.selected_item_id()
        if item_id is None:
            return
        item = self.database.get_inventory_item(item_id)
        profile = self.database.get_recommendation_profile(item_id)
        if item is None:
            self.refresh_items()
            return
        dialog = RecommendationProfileDialog(self, item, profile)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.save_recommendation_profile(item_id, dialog.values())
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self._selection_changed()

    def remove_recommendation_profile(self) -> None:
        item_id = self.selected_item_id()
        if item_id is None:
            return
        answer = QMessageBox.question(
            self,
            "Gỡ cấu hình gợi ý",
            "Gỡ sản phẩm khỏi hệ thống gợi ý? Thông tin tồn kho không bị xóa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.database.delete_recommendation_profile(item_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self._selection_changed()

    def open_recommendations(self) -> None:
        RecommendationsDialog(self, self.database).exec()

    def open_advisor(self) -> None:
        PetAdvisorDialog(self, self.database).exec()

    def open_recommendation_evaluation(self) -> None:
        RecommendationEvaluationDialog(self, self.database).exec()

    def add_item(self) -> None:
        dialog = InventoryItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_item(dialog.values())

    def edit_item(self) -> None:
        item_id = self.selected_item_id()
        item = (
            self.database.get_inventory_item(item_id)
            if item_id is not None
            else None
        )
        if item is None:
            return
        dialog = InventoryItemDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_item(dialog.values(), item_id)

    def _save_item(self, values: dict[str, Any], item_id: int | None = None) -> None:
        try:
            self.database.save_inventory_item(values, item_id)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self.refresh_items()

    def receive_stock(self) -> None:
        item_id = self.selected_item_id()
        item = (
            self.database.get_inventory_item(item_id)
            if item_id is not None
            else None
        )
        if item is None:
            return
        dialog = ReceiveStockDialog(self, item["unit"])
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.receive_inventory_stock(item_id, dialog.values())
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self.refresh_items()

    def consume_stock(self) -> None:
        item_id = self.selected_item_id()
        item = (
            self.database.get_inventory_item(item_id)
            if item_id is not None
            else None
        )
        if item is None:
            return
        dialog = ConsumeStockDialog(self, item["unit"], self.database.list_animals())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.consume_inventory_stock(item_id, dialog.values())
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self.refresh_items()

    def toggle_active(self) -> None:
        item_id = self.selected_item_id()
        item = (
            self.database.get_inventory_item(item_id)
            if item_id is not None
            else None
        )
        if item is None:
            return
        active = not bool(item["is_active"])
        action = "kích hoạt lại" if active else "ngừng sử dụng"
        answer = QMessageBox.question(
            self,
            "Cập nhật vật tư",
            f"Bạn có chắc muốn {action} vật tư này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.database.set_inventory_item_active(item_id, active)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._show_error(error)
            return
        self.refresh_items()

    def _show_error(self, error: Exception) -> None:
        detail = str(error)
        if isinstance(error, sqlite3.IntegrityError):
            message = (
                "Mã vật tư đã tồn tại."
                if "inventory_items.item_code" in detail
                else "Mã lô này đã tồn tại cho vật tư."
            )
        else:
            message = detail
        QMessageBox.warning(self, "Không thể thực hiện", message)
