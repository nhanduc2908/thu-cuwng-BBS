from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import make_table, set_cell


class OperationsPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.settings_enabled = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Cảnh báo và vận hành", objectName="pageTitle"))

        self.summary_cards = {}
        summary_row = QHBoxLayout()
        for key, title, color in (
            ("total", "Tổng cảnh báo", "#2d7d42"),
            ("high", "Khẩn cấp", "#b33636"),
            ("vaccination", "Tiêm phòng", "#5976b8"),
            ("care", "Chăm sóc", "#9b5f17"),
        ):
            card = QWidget()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            label = QLabel(title)
            value = QLabel("0")
            value.setObjectName("statValue")
            value.setStyleSheet(f"color: {color};")
            card_layout.addWidget(label)
            card_layout.addWidget(value)
            summary_row.addWidget(card)
            self.summary_cards[key] = value
        layout.addLayout(summary_row)

        self.tabs = QTabWidget()
        self.alerts_tab = QWidget()
        alerts_layout = QVBoxLayout(self.alerts_tab)
        toolbar = QHBoxLayout()
        self.refresh_button = QPushButton("Làm mới cảnh báo")
        self.refresh_button.clicked.connect(self.refresh_alerts)
        toolbar.addWidget(self.refresh_button)
        toolbar.addStretch(1)
        alerts_layout.addLayout(toolbar)
        self.alerts_table = make_table(
            ["Mức độ", "Nhóm", "Cảnh báo", "Chi tiết", "Ngày"]
        )
        alerts_layout.addWidget(self.alerts_table)

        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        settings_layout.addWidget(
            QLabel(
                "Sao lưu tạo bản SQLite nhất quán. Bản sao lưu mới luôn được lưu "
                "thành tệp riêng, không ghi đè bản trước."
            )
        )
        settings_toolbar = QHBoxLayout()
        settings_toolbar.addStretch(1)
        self.choose_directory_button = QPushButton("Chọn thư mục sao lưu")
        self.choose_directory_button.clicked.connect(self.choose_backup_directory)
        self.backup_button = QPushButton("Sao lưu ngay", objectName="primaryButton")
        self.backup_button.clicked.connect(self.create_backup)
        settings_toolbar.addWidget(self.choose_directory_button)
        settings_toolbar.addWidget(self.backup_button)
        settings_layout.addLayout(settings_toolbar)
        self.backup_location = QLabel()
        self.backup_location.setWordWrap(True)
        settings_layout.addWidget(self.backup_location)
        settings_layout.addStretch(1)

        self.tabs.addTab(self.alerts_tab, "Cảnh báo")
        self.tabs.addTab(self.settings_tab, "Thiết lập & sao lưu")
        layout.addWidget(self.tabs)
        self.refresh()

    def set_section(self, section: str) -> None:
        section_indexes = {"notifications": 0, "settings": 1}
        if section not in section_indexes:
            raise ValueError(f"Phân hệ vận hành không hợp lệ: {section}")
        self.tabs.setCurrentIndex(section_indexes[section])

    def set_settings_enabled(self, enabled: bool) -> None:
        self.settings_enabled = enabled
        self.tabs.tabBar().setTabVisible(1, enabled)
        self.choose_directory_button.setEnabled(enabled)
        self.backup_button.setEnabled(enabled)

    def refresh(self, *_: object) -> None:
        self.refresh_alerts()
        self._refresh_backup_location()

    def refresh_alerts(self) -> None:
        alerts = self.database.list_operational_alerts()
        summary = self.database.notifications.get_alert_summary()
        for key, value in self.summary_cards.items():
            value.setText(str(summary.get(key, 0)))

        self.alerts_table.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            set_cell(
                self.alerts_table,
                row,
                0,
                "Cao" if alert["severity"] == "HIGH" else "Trung bình",
            )
            set_cell(self.alerts_table, row, 1, alert["category"])
            set_cell(self.alerts_table, row, 2, alert["title"])
            set_cell(self.alerts_table, row, 3, alert["detail"])
            set_cell(self.alerts_table, row, 4, alert["date"])
            if alert["severity"] == "HIGH":
                for column in range(self.alerts_table.columnCount()):
                    item = self.alerts_table.item(row, column)
                    if item:
                        item.setForeground(Qt.GlobalColor.darkRed)

    def _default_backup_directory(self) -> Path:
        configured = self.database.get_setting("backup_directory")
        if configured:
            return Path(configured)
        return self.database.path.parent / "backups"

    def _refresh_backup_location(self) -> None:
        self.backup_location.setText(
            f"Thư mục sao lưu: {self._default_backup_directory()}"
        )

    def choose_backup_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục sao lưu",
            str(self._default_backup_directory()),
        )
        if not directory:
            return
        try:
            self.database.save_setting("backup_directory", str(Path(directory)))
        except (ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể lưu thiết lập", str(error))
            return
        self._refresh_backup_location()

    def create_backup(self) -> None:
        directory = self._default_backup_directory()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            filename = f"pet_store_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
            destination = self.database.backup_to(directory / filename)
        except (OSError, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể sao lưu", str(error))
            return
        QMessageBox.information(
            self, "Sao lưu hoàn tất", f"Bản sao lưu được lưu tại:\n{destination}"
        )
