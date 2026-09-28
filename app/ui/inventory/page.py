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
    ReceiveStockDialog,
)


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
        for button in (
            self.add_button,
            self.edit_button,
            self.receive_button,
            self.consume_button,
            self.active_button,
        ):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)

        self.items_table = make_table(
            [
                "Mã",
                "Vật tư",
                "Loại",
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
        ):
            button.setVisible(enabled)

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
            set_cell(self.items_table, row, 1, item["name"])
            set_cell(
                self.items_table,
                row,
                2,
                INVENTORY_CATEGORY_LABELS[item["category"]],
            )
            set_cell(
                self.items_table,
                row,
                3,
                f"{item['usable_quantity']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                4,
                f"{item['stock_quantity']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                5,
                f"{item['minimum_stock']:g} {item['unit']}",
            )
            set_cell(
                self.items_table,
                row,
                6,
                f"{item['expired_quantity']:g} {item['unit']}",
            )
            set_cell(self.items_table, row, 7, item["unit"])
            set_cell(
                self.items_table,
                row,
                8,
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
                INVENTORY_MOVEMENT_LABELS[movement["movement_type"]],
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
