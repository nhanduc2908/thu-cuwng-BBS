from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table, set_cell
from scripts.import_html_data_to_sqlite import import_sources, load_json_sources


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIRECTORY = PROJECT_ROOT / "HTML" / "data"
DEFAULT_REFERENCE_DATABASE = DEFAULT_DATA_DIRECTORY / "petcare_reference.sqlite"
CLASSIFICATION_LABELS = {
    "synthetic_demo": "Dữ liệu demo tổng hợp",
    "generated_catalog": "Catalog tạo tự động · chưa xác minh",
    "unverified": "Chưa xác minh nguồn",
}


class DataCatalogPage(QWidget):
    def __init__(self, database: Database, can_import: bool) -> None:
        super().__init__()
        self.database = database
        self.can_import = can_import
        self.sources: list[dict[str, Any]] = []
        self.selected_source: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("JSON dùng chung · chuyển dữ liệu SQLite", objectName="pageTitle"))
        layout.addWidget(
            QLabel(
                "Đọc cùng bộ HTML/data JSON mà website sử dụng, xem nguồn và kiểm tra trước khi đưa vào SQLite staging. "
                "Không ghi các bản ghi demo vào bảng nghiệp vụ."
            )
        )

        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Thư mục JSON"))
        self.source_directory = QLineEdit(str(DEFAULT_DATA_DIRECTORY))
        self.source_directory.setReadOnly(True)
        self.browse_source_button = QPushButton("Chọn thư mục")
        self.browse_source_button.clicked.connect(self.choose_source_directory)
        source_row.addWidget(self.source_directory, 1)
        source_row.addWidget(self.browse_source_button)
        layout.addLayout(source_row)

        destination_row = QHBoxLayout()
        destination_row.addWidget(QLabel("SQLite staging"))
        self.destination_path = QLineEdit(str(DEFAULT_REFERENCE_DATABASE))
        self.destination_path.setReadOnly(True)
        self.browse_destination_button = QPushButton("Chọn tệp")
        self.browse_destination_button.clicked.connect(self.choose_destination)
        destination_row.addWidget(self.destination_path, 1)
        destination_row.addWidget(self.browse_destination_button)
        layout.addLayout(destination_row)

        warning = QLabel(
            "CẢNH BÁO: Dữ liệu module/bệnh lý là tổng hợp; catalog dinh dưỡng được tạo tự động và chưa xác minh. "
            "Chỉ nhập vào kho staging riêng, không dùng làm hồ sơ thật, giá thật hay tư vấn thú y."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(
            "QLabel { background: #fff5df; color: #765620; border: 1px solid #ead7aa; "
            "border-radius: 8px; padding: 9px; }"
        )
        layout.addWidget(warning)

        controls = QHBoxLayout()
        controls.addStretch(1)
        self.scan_button = QPushButton("Kiểm tra nguồn JSON")
        self.scan_button.clicked.connect(self.scan_sources)
        controls.addWidget(self.scan_button)
        self.import_button = QPushButton("Nhập / cập nhật SQLite staging")
        self.import_button.setObjectName("primaryButton")
        self.import_button.setEnabled(can_import)
        self.import_button.setToolTip(
            "" if can_import else "Cần quyền settings.manage để nhập dữ liệu."
        )
        self.import_button.clicked.connect(self.import_to_sqlite)
        controls.addWidget(self.import_button)
        layout.addLayout(controls)

        self.status = QLabel("Chọn “Kiểm tra nguồn JSON” để xác thực danh mục và các tệp.")
        self.status.setWordWrap(True)
        self.status.setObjectName("pageSubtitle")
        layout.addWidget(self.status)

        self.source_table = make_table(
            ["Tệp JSON", "Phân loại", "Bản ghi", "Chồng lặp", "SHA-256"]
        )
        self.source_table.currentCellChanged.connect(self._source_selected)
        layout.addWidget(self.source_table, 2)

        layout.addWidget(QLabel("Xem trước bản ghi (tối đa 20 dòng)", objectName="sectionTitle"))
        self.preview = make_table(["Đang chờ chọn nguồn"])
        layout.addWidget(self.preview, 2)

        self._set_import_controls(can_import)

    def refresh(self, *_: object) -> None:
        self.scan_sources()

    def _set_import_controls(self, enabled: bool) -> None:
        self.import_button.setEnabled(enabled)
        self.browse_source_button.setEnabled(enabled)
        self.browse_destination_button.setEnabled(enabled)

    def set_import_enabled(self, enabled: bool) -> None:
        self.can_import = enabled
        self._set_import_controls(enabled)
        self.import_button.setToolTip(
            "" if enabled else "Cần quyền settings.manage để nhập dữ liệu."
        )

    def choose_source_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục JSON", self.source_directory.text()
        )
        if not directory:
            return
        self.source_directory.setText(directory)
        self.scan_sources()

    def choose_destination(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Chọn SQLite staging",
            self.destination_path.text(),
            "SQLite database (*.sqlite *.db);;All files (*)",
        )
        if filename:
            self.destination_path.setText(filename)

    def scan_sources(self) -> None:
        try:
            self.sources = load_json_sources(Path(self.source_directory.text()))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self.sources = []
            self.source_table.setRowCount(0)
            self.preview.setRowCount(0)
            self.status.setText(f"Không thể xác thực dữ liệu JSON: {error}")
            QMessageBox.warning(self, "Nguồn JSON không hợp lệ", str(error))
            return

        self.source_table.setRowCount(len(self.sources))
        total_records = 0
        for row, source in enumerate(self.sources):
            total_records += source["record_count"]
            set_cell(self.source_table, row, 0, source["source_file"])
            set_cell(
                self.source_table,
                row,
                1,
                CLASSIFICATION_LABELS.get(
                    source["classification"], CLASSIFICATION_LABELS["unverified"]
                ),
            )
            set_cell(self.source_table, row, 2, source["record_count"])
            set_cell(
                self.source_table,
                row,
                3,
                "Có · nguồn tổng hợp" if source["is_derived"] else "Không",
            )
            set_cell(self.source_table, row, 4, source["sha256"][:16])
            file_item = self.source_table.item(row, 0)
            if file_item is not None:
                file_item.setData(Qt.ItemDataRole.UserRole, row)

        self.status.setText(
            f"Đã kiểm tra {len(self.sources)} nguồn JSON · {total_records:,} bản ghi "
            "trong các mảng đối tượng. Chọn một nguồn để xem trước."
        )
        if self.sources:
            self.source_table.selectRow(0)
        else:
            self.preview.setRowCount(0)

    def _source_selected(
        self, row: int, _column: int, _previous_row: int, _previous_column: int
    ) -> None:
        if row < 0 or row >= len(self.sources):
            return
        source = self.sources[row]
        self.selected_source = source
        arrays = source["arrays"]
        if source["array_path"]:
            arrays = [
                array for array in arrays
                if array["array_path"] == source["array_path"]
            ] or arrays
        if not arrays:
            self.preview.setColumnCount(1)
            self.preview.setHorizontalHeaderLabels(["Nội dung"])
            self.preview.setRowCount(1)
            set_cell(self.preview, 0, 0, "Tệp không chứa mảng bản ghi dạng object.")
            return

        records = arrays[0]["records"]
        fields = list(dict.fromkeys(
            field for record in records[:20] for field in record
        ))[:12]
        if not fields:
            fields = ["JSON"]
        self.preview.clear()
        self.preview.setColumnCount(len(fields))
        self.preview.setHorizontalHeaderLabels(fields)
        preview_rows = records[:20]
        self.preview.setRowCount(len(preview_rows))
        for preview_row, record in enumerate(preview_rows):
            for column, field in enumerate(fields):
                value = record.get(field)
                rendered = (
                    json.dumps(value, ensure_ascii=False)
                    if isinstance(value, (dict, list))
                    else "" if value is None else str(value)
                )
                set_cell(self.preview, preview_row, column, rendered)

    def import_to_sqlite(self) -> None:
        if not self.can_import:
            QMessageBox.warning(
                self, "Không đủ quyền", "Cần quyền settings.manage để nhập dữ liệu."
            )
            return
        self.scan_sources()
        if not self.sources:
            return
        destination = Path(self.destination_path.text())
        if destination.resolve() == self.database.path.resolve():
            QMessageBox.warning(
                self,
                "Không dùng cơ sở dữ liệu nghiệp vụ",
                "Hãy chọn một tệp SQLite staging riêng; không thể ghi catalog JSON vào database giao dịch.",
            )
            return
        confirmation = QMessageBox.question(
            self,
            "Xác nhận nhập JSON",
            f"Nhập hoặc cập nhật {len(self.sources)} nguồn vào:\n{destination}\n\n"
            "Các bảng staging được thay thế theo từng nguồn; bảng nghiệp vụ không bị chỉnh sửa.",
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        self.import_button.setEnabled(False)
        try:
            imported = import_sources(destination, self.sources)
            with sqlite3.connect(destination) as connection:
                source_count, record_count = connection.execute(
                    "SELECT COUNT(*), COALESCE(SUM(record_count), 0) "
                    "FROM html_data_sources"
                ).fetchone()
                integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
            if integrity != "ok":
                raise sqlite3.DatabaseError(
                    f"SQLite quick_check failed: {integrity}"
                )
        except (OSError, sqlite3.Error, ValueError) as error:
            self.status.setText(f"Không thể nhập JSON vào SQLite staging: {error}")
            QMessageBox.critical(self, "Nhập dữ liệu thất bại", str(error))
        else:
            self.status.setText(
                f"Đã nhập {imported:,} bản ghi từ {len(self.sources)} tệp. "
                f"SQLite staging hiện có {source_count} nguồn · {record_count:,} bản ghi; "
                f"kiểm tra toàn vẹn: {integrity}."
            )
            QMessageBox.information(
                self, "Nhập dữ liệu hoàn tất", self.status.text()
            )
        finally:
            self.import_button.setEnabled(self.can_import)
