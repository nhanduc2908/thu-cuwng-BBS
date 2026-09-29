from __future__ import annotations

import sqlite3
from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.recommendations.constants import RECOMMENDATION_EVENT_LABELS
from app.modules.recommendations.evaluation import evaluate_recommendations
from app.ui.common import make_table, set_cell


class RecommendationEvaluationDialog(QDialog):
    def __init__(self, parent: QWidget, database: Database) -> None:
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("AI Evaluation Lab · đánh giá gợi ý")
        self.setMinimumSize(780, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("ĐÁNH GIÁ HỆ THỐNG GỢI Ý", objectName="pageTitle")
        )
        layout.addWidget(
            QLabel(
                "Đánh giá ngoại tuyến bằng cách dùng 80% tương tác tích cực sớm "
                "làm dữ liệu đầu vào và giữ lại 20% cuối để kiểm tra Top-K. "
                "Chỉ tính thú cưng có tương tác phù hợp; kết quả dựa trên các lần "
                "VIEW/LIKE/Đã mua được nhân viên ghi nhận, không phải thử nghiệm "
                "ngẫu nhiên hay bằng chứng nhân quả."
            )
        )
        layout.addWidget(
            QLabel(
                "So sánh bộ xếp hạng hiện tại với baseline phổ biến nhất trên cùng "
                "tập sản phẩm đủ điều kiện (đã áp dụng lọc loài, tồn, dị ứng, giá "
                "và giới hạn đã cấu hình). Không dùng tín hiệu cộng tác tương lai. "
                "CTR, doanh thu tăng thêm, độ chính xác sức khỏe, hallucination và "
                "confidence calibration không được suy ra vì hệ thống chưa lưu "
                "impression/session hoặc nhãn đánh giá độc lập."
            )
        )

        self.summary = QLabel("Chưa chạy đánh giá.")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.table = make_table(["Chỉ số", "Baseline phổ biến", "Hybrid hiện tại"])
        layout.addWidget(self.table, 1)

        self.events_table = make_table(["Tương tác đã ghi nhận", "Số lượt"])
        layout.addWidget(self.events_table, 1)
        actions = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.run_button = QPushButton("Chạy lại đánh giá")
        self.run_button.clicked.connect(self.run_evaluation)
        actions.addButton(self.run_button, QDialogButtonBox.ButtonRole.ActionRole)
        actions.rejected.connect(self.reject)
        actions.accepted.connect(self.accept)
        layout.addWidget(actions)
        self.run_evaluation()

    def run_evaluation(self) -> None:
        self.run_button.setEnabled(False)
        try:
            products = [
                dict(item) for item in self.database.list_recommendation_products()
            ]
            animals = {
                int(animal["id"]): dict(animal)
                for animal in self.database.list_animals()
            }
            interactions = {
                animal_id: self.database.list_recommendation_interactions(animal_id)
                for animal_id in animals
            }
            result = evaluate_recommendations(products, animals, interactions, k=5)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self.summary.setText(f"Không thể chạy đánh giá AI: {error}")
            return
        finally:
            self.run_button.setEnabled(True)

        self.summary.setText(
            f"Mẫu đủ điều kiện: {result['sample_count']} thú cưng · "
            f"Bỏ qua do thiếu dữ liệu: {result['skipped_animals']} · "
            f"Danh mục đủ điều kiện: {result['eligible_item_count']} sản phẩm · "
            f"Độ phủ Top-5: baseline {result['baseline_catalog_coverage']:.1%}, "
            f"hybrid {result['catalog_coverage']:.1%} · "
            f"Latency trung bình hybrid: {result['mean_latency_ms']:.2f} ms. "
            "Nếu mẫu bằng 0 thì không có đủ lịch sử để kết luận chất lượng."
        )
        metrics = (
            ("Precision@5", "precision"),
            ("Recall@5", "recall"),
            ("NDCG@5", "ndcg"),
            ("MRR@5", "mrr"),
        )
        self.table.setRowCount(len(metrics) + 2)
        for row, (label, key) in enumerate(metrics):
            set_cell(self.table, row, 0, label)
            set_cell(self.table, row, 1, f"{result['baseline'][key]:.3f}")
            set_cell(self.table, row, 2, f"{result['hybrid'][key]:.3f}")
        set_cell(self.table, 4, 0, "Novelty hybrid (bit)")
        set_cell(self.table, 4, 1, "—")
        set_cell(self.table, 4, 2, f"{result['novelty']:.3f}")
        set_cell(self.table, 5, 0, "Diversity hybrid (0–1)")
        set_cell(self.table, 5, 1, "—")
        set_cell(self.table, 5, 2, f"{result['diversity']:.3f}")

        event_counts = result["event_counts"]
        labels = RECOMMENDATION_EVENT_LABELS
        known_events = [
            (labels[event], count)
            for event, count in event_counts.items()
            if event in labels
        ]
        known_events.sort(key=lambda item: (-item[1], item[0]))
        self.events_table.setRowCount(len(known_events))
        for row, (label, count) in enumerate(known_events):
            set_cell(self.events_table, row, 0, label)
            set_cell(self.events_table, row, 1, str(count))
