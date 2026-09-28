import sqlite3
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database import Database


class PlatformPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Nền tảng hệ thống", objectName="pageTitle"))
        layout.addWidget(
            QLabel(
                "Thông tin môi trường chạy ứng dụng, cơ sở dữ liệu và trạng thái kết nối."
            )
        )

        self.cards: dict[str, QLabel] = {}
        grid = QGridLayout()
        definitions = (
            ("python", "Python"),
            ("qt", "Giao diện"),
            ("sqlite", "Cơ sở dữ liệu"),
            ("storage", "Dung lượng dữ liệu"),
            ("animals", "Hồ sơ động vật"),
            ("users", "Tài khoản"),
        )
        for index, (key, title) in enumerate(definitions):
            card = QFrame(objectName="statCard")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(title, objectName="sectionTitle"))
            value = QLabel("—", objectName="statValue")
            value.setWordWrap(True)
            card_layout.addWidget(value)
            self.cards[key] = value
            grid.addWidget(card, index // 3, index % 3)
        layout.addLayout(grid)

        path_heading = QLabel("Vị trí cơ sở dữ liệu", objectName="sectionTitle")
        layout.addWidget(path_heading)
        self.path_label = QLabel()
        self.path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
        controls = QHBoxLayout()
        controls.addStretch(1)
        self.refresh_button = QPushButton("Làm mới trạng thái")
        self.refresh_button.clicked.connect(self.refresh)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)
        layout.addStretch(1)
        self.refresh()

    def refresh(self, *_: object) -> None:
        self.cards["python"].setText(sys.version.split()[0])
        self.cards["qt"].setText("PySide6")
        self.cards["sqlite"].setText(sqlite3.sqlite_version)
        self.path_label.setText(str(self.database.path.resolve()))
        try:
            size = self.database.path.stat().st_size
            self.cards["storage"].setText(f"{size / (1024 * 1024):.2f} MB")
            self.cards["animals"].setText(
                str(self.database.dashboard_counts()["TOTAL"])
            )
            self.cards["users"].setText(str(self.database.user_count()))
        except OSError as error:
            self.cards["storage"].setText("Không đọc được")
            self.cards["storage"].setToolTip(str(error))
