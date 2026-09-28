from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.ui.common import STATUS_LABELS, make_table, set_cell


class DashboardPage(QWidget):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(QLabel("Tổng quan cửa hàng", objectName="pageTitle"))
        layout.addWidget(
            QLabel("Theo dõi nhanh số lượng và tình trạng động vật hiện có.")
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
        layout.addWidget(QLabel("Động vật mới cập nhật", objectName="sectionTitle"))
        self.table = make_table(["Mã", "Tên", "Loài", "Trạng thái", "Ngày tạo"])
        layout.addWidget(self.table)
        layout.addStretch()

    def refresh(self) -> None:
        counts = self.database.dashboard_counts()
        for key, label in self.cards.items():
            label.setText(str(counts[key]))
        animals = self.database.recent_animals()
        self.table.setRowCount(len(animals))
        for row_number, animal in enumerate(animals):
            set_cell(self.table, row_number, 0, animal["animal_code"])
            set_cell(self.table, row_number, 1, animal["name"])
            set_cell(self.table, row_number, 2, animal["species"])
            set_cell(self.table, row_number, 3, STATUS_LABELS[animal["status"]])
            set_cell(self.table, row_number, 4, animal["created_at"][:10])
