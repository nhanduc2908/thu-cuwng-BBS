import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.imports.constants import (
    IMPORT_BATCH_STATUS_LABELS,
    INSPECTION_RESULT_LABELS,
)
from app.ui.common import make_table, set_cell
from app.ui.imports.dialogs import (
    ImportAnimalDialog,
    ImportBatchDialog,
    InspectionDialog,
    InspectionHistoryDialog,
    SupplierDialog,
)


class ImportsPage(QWidget):
    def __init__(
        self, database: Database, focused_section: str | None = None
    ) -> None:
        super().__init__()
        self.database = database
        self.manage_enabled = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        page_titles = {
            None: "Nhà cung cấp và nhập động vật",
            "suppliers": "Nhà cung cấp",
            "imports": "Nhập động vật & kiểm tra đầu vào",
        }
        if focused_section not in page_titles:
            raise ValueError(f"Phân hệ nhập hàng không hợp lệ: {focused_section}")
        layout.addWidget(
            QLabel(page_titles[focused_section], objectName="pageTitle")
        )
        self.tabs = QTabWidget()
        self.suppliers_tab = self._build_suppliers_tab()
        self.batches_tab = self._build_batches_tab()
        self.tabs.addTab(self.suppliers_tab, "Nhà cung cấp")
        self.tabs.addTab(self.batches_tab, "Lô nhập & kiểm tra")
        if focused_section is not None:
            section_index = {"suppliers": 0, "imports": 1}.get(focused_section)
            self.tabs.setCurrentIndex(section_index)
            self.tabs.tabBar().hide()
        layout.addWidget(self.tabs)
        self.refresh_suppliers()
        self.refresh_batches()

    def _build_suppliers_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        toolbar = QHBoxLayout()
        toolbar.addStretch()
        add = QPushButton("+ Thêm nhà cung cấp", objectName="primaryButton")
        add.clicked.connect(self.add_supplier)
        self.add_supplier_button = add
        toolbar.addWidget(add)
        layout.addLayout(toolbar)
        self.suppliers_table = make_table(
            ["Mã", "Nhà cung cấp", "Người liên hệ", "Điện thoại", "Email", "Số lô", "Trạng thái"]
        )
        layout.addWidget(self.suppliers_table)
        buttons = QHBoxLayout()
        buttons.addStretch()
        self.supplier_edit_button = QPushButton("Chỉnh sửa")
        self.supplier_edit_button.clicked.connect(self.edit_supplier)
        self.supplier_active_button = QPushButton("Ngừng hoạt động")
        self.supplier_active_button.clicked.connect(self.toggle_supplier_active)
        buttons.addWidget(self.supplier_edit_button)
        buttons.addWidget(self.supplier_active_button)
        layout.addLayout(buttons)
        self.suppliers_table.currentCellChanged.connect(
            self._supplier_selection_changed
        )
        return page

    def _build_batches_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        toolbar = QHBoxLayout()
        toolbar.addWidget(
            QLabel("Tạo lô nhập, lập hồ sơ cá thể rồi kiểm tra đầu vào.")
        )
        toolbar.addStretch()
        self.create_batch_button = QPushButton(
            "+ Tạo lô nhập", objectName="primaryButton"
        )
        self.create_batch_button.clicked.connect(self.create_batch)
        toolbar.addWidget(self.create_batch_button)
        layout.addLayout(toolbar)

        self.batches_table = make_table(
            ["Mã lô", "Nhà cung cấp", "Ngày nhập", "Số con", "Đã kiểm tra", "Trạng thái"]
        )
        self.batches_table.currentCellChanged.connect(self._batch_selection_changed)
        layout.addWidget(self.batches_table, 3)

        item_header = QHBoxLayout()
        item_header.addWidget(
            QLabel("Động vật trong lô", objectName="sectionTitle")
        )
        item_header.addStretch()
        self.add_animal_button = QPushButton("+ Thêm động vật")
        self.add_animal_button.setObjectName("manageImportButton")
        self.add_animal_button.clicked.connect(self.add_import_animal)
        self.inspect_button = QPushButton("Kiểm tra đầu vào")
        self.inspect_button.setObjectName("manageImportButton")
        self.inspect_button.clicked.connect(self.inspect_animal)
        self.history_button = QPushButton("Lịch sử kiểm tra")
        self.history_button.clicked.connect(self.show_inspection_history)
        for button in (
            self.add_animal_button,
            self.inspect_button,
            self.history_button,
        ):
            item_header.addWidget(button)
        layout.addLayout(item_header)
        self.batch_animals_table = make_table(
            ["Mã", "Tên", "Loài/giống", "Giá nhập", "Kết quả kiểm tra", "Trạng thái"]
        )
        self.batch_animals_table.currentCellChanged.connect(
            self._import_animal_selection_changed
        )
        layout.addWidget(self.batch_animals_table, 2)
        return page

    def set_manage_enabled(self, enabled: bool) -> None:
        self.add_supplier_button.setVisible(enabled)
        self.supplier_edit_button.setVisible(enabled)
        self.supplier_active_button.setVisible(enabled)
        self.create_batch_button.setVisible(enabled)
        self.add_animal_button.setVisible(enabled)
        self.inspect_button.setVisible(enabled)
        self.manage_enabled = enabled

    def selected_supplier_id(self) -> int | None:
        row = self.suppliers_table.currentRow()
        if row < 0 or self.suppliers_table.item(row, 0) is None:
            return None
        return self.suppliers_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def selected_batch_id(self) -> int | None:
        row = self.batches_table.currentRow()
        if row < 0 or self.batches_table.item(row, 0) is None:
            return None
        return self.batches_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def selected_import_animal_id(self) -> int | None:
        row = self.batch_animals_table.currentRow()
        if row < 0 or self.batch_animals_table.item(row, 0) is None:
            return None
        return self.batch_animals_table.item(row, 0).data(
            Qt.ItemDataRole.UserRole
        )

    def refresh_suppliers(self) -> None:
        suppliers = self.database.list_suppliers()
        self.suppliers_table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            set_cell(self.suppliers_table, row, 0, supplier["supplier_code"])
            self.suppliers_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, supplier["id"]
            )
            set_cell(self.suppliers_table, row, 1, supplier["name"])
            set_cell(self.suppliers_table, row, 2, supplier["contact_person"])
            set_cell(self.suppliers_table, row, 3, supplier["phone"])
            set_cell(self.suppliers_table, row, 4, supplier["email"])
            set_cell(self.suppliers_table, row, 5, supplier["batch_count"])
            set_cell(
                self.suppliers_table,
                row,
                6,
                "Đang hoạt động" if supplier["is_active"] else "Ngừng hoạt động",
            )
        if suppliers and self.suppliers_table.currentRow() < 0:
            self.suppliers_table.selectRow(0)
        self._supplier_selection_changed()

    def refresh_batches(self, *_: Any) -> None:
        selected = self.selected_batch_id()
        batches = self.database.list_import_batches()
        self.batches_table.setRowCount(len(batches))
        selected_row = -1
        for row, batch in enumerate(batches):
            set_cell(self.batches_table, row, 0, batch["batch_code"])
            self.batches_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, batch["id"]
            )
            if batch["id"] == selected:
                selected_row = row
            set_cell(
                self.batches_table,
                row,
                1,
                f"{batch['supplier_code']} — {batch['supplier_name']}",
            )
            set_cell(self.batches_table, row, 2, batch["import_date"])
            set_cell(self.batches_table, row, 3, batch["animal_count"])
            set_cell(self.batches_table, row, 4, batch["inspected_count"])
            set_cell(
                self.batches_table,
                row,
                5,
                IMPORT_BATCH_STATUS_LABELS[batch["status"]],
            )
        if selected_row >= 0:
            self.batches_table.selectRow(selected_row)
        elif batches:
            self.batches_table.selectRow(0)
        else:
            self.batch_animals_table.setRowCount(0)
            self._batch_selection_changed()

    def _supplier_selection_changed(self, *_: Any) -> None:
        supplier_id = self.selected_supplier_id()
        supplier = (
            self.database.get_supplier(supplier_id) if supplier_id is not None else None
        )
        self.supplier_edit_button.setEnabled(
            supplier is not None and self.manage_enabled
        )
        self.supplier_active_button.setEnabled(
            supplier is not None and self.manage_enabled
        )
        self.supplier_active_button.setText(
            "Ngừng hoạt động"
            if supplier is not None and supplier["is_active"]
            else "Kích hoạt lại"
        )

    def _batch_selection_changed(self, *_: Any) -> None:
        batch_id = self.selected_batch_id()
        self.batch_animals_table.setRowCount(0)
        batch = self.database.list_import_batches()
        selected_batch = next(
            (item for item in batch if item["id"] == batch_id), None
        )
        self.add_animal_button.setEnabled(
            self.manage_enabled
            and selected_batch is not None
            and selected_batch["status"] == "OPEN"
        )
        self.inspect_button.setEnabled(
            self.manage_enabled and selected_batch is not None
        )
        if batch_id is None:
            self.history_button.setEnabled(False)
            return
        for row, animal in enumerate(self.database.list_import_animals(batch_id)):
            self.batch_animals_table.insertRow(row)
            set_cell(self.batch_animals_table, row, 0, animal["animal_code"])
            self.batch_animals_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, animal["id"]
            )
            set_cell(self.batch_animals_table, row, 1, animal["name"])
            breed = f" / {animal['breed']}" if animal["breed"] else ""
            set_cell(
                self.batch_animals_table,
                row,
                2,
                f"{animal['species']}{breed}",
            )
            set_cell(
                self.batch_animals_table,
                row,
                3,
                f"{animal['purchase_price']:,.0f} ₫",
            )
            result = animal["inspection_result"]
            set_cell(
                self.batch_animals_table,
                row,
                4,
                INSPECTION_RESULT_LABELS.get(result, "Chưa kiểm tra"),
            )
            set_cell(
                self.batch_animals_table,
                row,
                5,
                self._animal_status_label(animal["status"]),
            )
        self._import_animal_selection_changed()

    def _import_animal_selection_changed(self, *_: Any) -> None:
        self.history_button.setEnabled(
            self.selected_import_animal_id() is not None
        )
        self.history_button.setVisible(
            self.selected_import_animal_id() is not None
        )

    def _animal_status_label(self, status: str) -> str:
        from app.ui.common import STATUS_LABELS

        return STATUS_LABELS.get(status, status)

    def add_supplier(self) -> None:
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_supplier(dialog.values())

    def edit_supplier(self) -> None:
        supplier_id = self.selected_supplier_id()
        if supplier_id is None:
            return
        supplier = self.database.get_supplier(supplier_id)
        if supplier is None:
            self.refresh_suppliers()
            return
        dialog = SupplierDialog(self, supplier)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_supplier(dialog.values(), supplier_id)

    def _save_supplier(
        self, values: dict[str, Any], supplier_id: int | None = None
    ) -> None:
        try:
            self.database.save_supplier(values, supplier_id)
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_suppliers()
        self.refresh_batches()

    def toggle_supplier_active(self) -> None:
        supplier_id = self.selected_supplier_id()
        if supplier_id is None:
            return
        supplier = self.database.get_supplier(supplier_id)
        if supplier is None:
            self.refresh_suppliers()
            return
        try:
            self.database.set_supplier_active(
                supplier_id, not bool(supplier["is_active"])
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_suppliers()

    def create_batch(self) -> None:
        suppliers = [
            supplier
            for supplier in self.database.list_suppliers()
            if supplier["is_active"]
        ]
        if not suppliers:
            QMessageBox.information(
                self,
                "Chưa có nhà cung cấp",
                "Hãy thêm và kích hoạt nhà cung cấp trước khi tạo lô nhập.",
            )
            self.tabs.setCurrentWidget(self.suppliers_tab)
            return
        dialog = ImportBatchDialog(self, suppliers)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.create_import_batch(dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_batches()

    def add_import_animal(self) -> None:
        batch_id = self.selected_batch_id()
        if batch_id is None:
            QMessageBox.information(self, "Chọn lô nhập", "Chọn lô cần ghi nhận động vật.")
            return
        dialog = ImportAnimalDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.add_import_animal(batch_id, dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_batches()

    def inspect_animal(self) -> None:
        batch_id = self.selected_batch_id()
        if batch_id is None:
            QMessageBox.information(self, "Chọn lô nhập", "Chọn lô cần kiểm tra.")
            return
        animals = [
            animal
            for animal in self.database.list_import_animals(batch_id)
            if animal["inspection_result"] is None
        ]
        if not animals:
            QMessageBox.information(
                self,
                "Không còn hồ sơ chờ",
                "Các động vật trong lô đã được kiểm tra. Có thể chọn hồ sơ để xem lịch sử.",
            )
            return
        dialog = InspectionDialog(self, animals)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.record_inspection(batch_id, dialog.values())
        except (sqlite3.Error, ValueError) as error:
            self._show_error(error)
            return
        self.refresh_batches()

    def show_inspection_history(self) -> None:
        batch_id = self.selected_batch_id()
        animal_id = self.selected_import_animal_id()
        if batch_id is None or animal_id is None:
            return
        InspectionHistoryDialog(
            self, self.database, batch_id, animal_id
        ).exec()

    def _show_error(self, error: Exception) -> None:
        message = str(error)
        if isinstance(error, sqlite3.IntegrityError):
            detail = str(error)
            if "suppliers.supplier_code" in detail:
                message = "Mã nhà cung cấp đã tồn tại."
            elif "import_batches.batch_code" in detail:
                message = "Mã lô nhập đã tồn tại."
            elif "animals.animal_code" in detail:
                message = "Mã động vật đã tồn tại."
        QMessageBox.warning(self, "Không thể thực hiện", message)
