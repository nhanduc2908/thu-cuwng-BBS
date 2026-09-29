from __future__ import annotations

from datetime import date
import html
import json
import re
import sqlite3
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.database import Database
from app.modules.recommendations.advisor import (
    build_budget_combo,
    extract_message_facts,
    extract_order_code,
    normalize_message_text,
    predict_replenishments,
)
from app.modules.recommendations.constants import (
    RECOMMENDATION_CATEGORY_LABELS,
    RECOMMENDATION_EVENT_LABELS,
)
from app.modules.recommendations.engine import recommend_products
from app.modules.sales.constants import ORDER_STATUS_LABELS
from app.ui.care.dialogs import CareTaskDialog
from app.ui.common import make_table, set_cell


def _decode_tag_set(value: str | None) -> set[str]:
    if not value:
        return set()
    decoded = json.loads(value)
    if not isinstance(decoded, list) or any(not isinstance(tag, str) for tag in decoded):
        raise ValueError("Thẻ giống trong hồ sơ sản phẩm bị lỗi.")
    return set(decoded)


class PetAdvisorDialog(QDialog):
    """Offline conversational assistant grounded in the local pet/shop database."""

    def __init__(self, parent: QWidget, database: Database) -> None:
        super().__init__(parent)
        self.database = database
        self.context: dict[str, Any] = {}
        self.results: list[dict[str, Any]] = []
        self.saved_animal_id: int | None = None
        self.setWindowTitle("AI PetCare Advisor · trợ lý ngoại tuyến")
        self.setMinimumSize(1000, 740)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("🐾 AI PETCARE ADVISOR", objectName="pageTitle"))
        root.addWidget(
            QLabel(
                "Trợ lý chạy cục bộ, đọc sản phẩm/giá/tồn từ SQLite và giải thích "
                "theo luật; không gửi hồ sơ hay hội thoại ra ngoài và không tự tạo "
                "hóa đơn. Có thể mô tả tự nhiên, ví dụ: “Mochi là Corgi cái, 4 tháng, "
                "6kg, da nhạy cảm; tìm thức ăn dưới 500k”."
            )
        )

        pet_row = QHBoxLayout()
        pet_row.addWidget(QLabel("Dùng hồ sơ có sẵn (tùy chọn):"))
        self.saved_pet = QComboBox()
        self.saved_pet.addItem("Dùng thông tin mô tả trong chat", None)
        for animal in database.list_animals():
            animal_id = int(animal["id"])
            self.saved_pet.addItem(
                f"{animal['animal_code']} — {animal['name']} ({animal['species']})",
                animal_id,
            )
        pet_row.addWidget(self.saved_pet, 1)
        root.addLayout(pet_row)

        self.transcript = QTextBrowser()
        self.transcript.setOpenExternalLinks(False)
        self.transcript.setMinimumHeight(250)
        self.transcript.setStyleSheet(
            "background: #fffdf9; border: 1px solid #e8e1d5; border-radius: 10px;"
        )
        root.addWidget(self.transcript, 2)
        self._append_message(
            "assistant",
            "Xin chào! Bạn có thể hỏi sản phẩm, tạo combo theo ngân sách, kiểm tra "
            "tồn kho, hỏi hướng dẫn chăm sóc chung hoặc tra mã đơn thú cưng. "
            "Nếu chưa có hồ sơ, hãy cho mình biết bé là chó, mèo hay loài nào nhé.",
        )

        self.product_table = make_table(
            ["Sản phẩm", "Nhóm", "Phù hợp", "Lý do", "Giá", "Tồn"]
        )
        self.product_table.currentCellChanged.connect(self._selection_changed)
        self.saved_pet.currentIndexChanged.connect(self._saved_pet_changed)
        root.addWidget(self.product_table, 2)
        self.response_detail = QLabel("")
        self.response_detail.setWordWrap(True)
        root.addWidget(self.response_detail)

        self.notice = QLabel(
            "Sức khỏe: đây không phải chẩn đoán. Khó thở, co giật, ngất, chảy máu "
            "hoặc triệu chứng nặng cần liên hệ bác sĩ thú y/cơ sở cấp cứu thú y."
        )
        self.notice.setWordWrap(True)
        self.notice.setStyleSheet("color: #9c4d3d; font-weight: 600;")
        root.addWidget(self.notice)

        actions = QHBoxLayout()
        self.action_buttons: list[QPushButton] = []
        for label, event in (
            ("Đã xem", "VIEW"),
            ("Quan tâm", "CLICK"),
            ("Thích", "LIKE"),
            ("Ghi nhận thêm giỏ", "ADD_TO_CART"),
            ("Ghi nhận đã mua", "PURCHASE"),
        ):
            button = QPushButton(label)
            button.setEnabled(False)
            button.clicked.connect(
                lambda _checked=False, event_type=event: self.record_event(event_type)
            )
            self.action_buttons.append(button)
            actions.addWidget(button)
        self.create_task_button = QPushButton("Tạo lịch chăm sóc")
        self.create_task_button.setEnabled(
            database.actor_id is not None
            and database.has_permission(database.actor_id, "care.manage")
        )
        self.create_task_button.clicked.connect(self.create_care_task)
        actions.addWidget(self.create_task_button)
        root.addLayout(actions)

        composer = QHBoxLayout()
        self.message = QLineEdit()
        self.message.setPlaceholderText("Nhập câu hỏi bằng tiếng Việt…")
        self.message.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Gửi", objectName="primaryButton")
        self.send_button.clicked.connect(self.send_message)
        composer.addWidget(self.message, 1)
        composer.addWidget(self.send_button)
        root.addLayout(composer)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        root.addWidget(buttons)

    def _append_message(self, speaker: str, message: str) -> None:
        label = "Bạn" if speaker == "user" else "Trợ lý"
        color = "#d7775c" if speaker == "user" else "#2d634c"
        self.transcript.append(
            f'<p style="margin:8px 4px"><b style="color:{color}">'
            f"{label}:</b> {html.escape(message).replace(chr(10), '<br>')}</p>"
        )
        scrollbar = self.transcript.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _known_breeds(self, products: list[dict[str, Any]]) -> set[str]:
        breeds: set[str] = set()
        for product in products:
            breeds.update(_decode_tag_set(product.get("breed_tags")))
        return breeds

    def _current_pet(self) -> dict[str, Any] | None:
        animal_id = self.saved_pet.currentData()
        if animal_id is not None:
            animal = self.database.get_animal(int(animal_id))
            if animal is None:
                return None
            self.saved_animal_id = int(animal_id)
            pet = dict(animal)
        else:
            self.saved_animal_id = None
            pet = {}
        if animal_id is None:
            for key in ("species", "breed", "gender", "birth_date", "weight"):
                if key in self.context:
                    pet[key] = self.context[key]
        for key in ("allergies", "exercise_needs", "behavior", "health_status"):
            if key in self.context:
                pet[key] = self.context[key]
        if not pet.get("species"):
            return None
        return pet

    def _saved_pet_changed(self, *_: Any) -> None:
        self.context.clear()
        self.saved_animal_id = None
        self.results.clear()
        self.product_table.setRowCount(0)
        self.response_detail.clear()
        self._set_actions_enabled(False)
        animal_id = self.saved_pet.currentData()
        if animal_id is not None:
            self.saved_animal_id = int(animal_id)
            preferences = self.database.list_animal_product_preferences(
                self.saved_animal_id
            )
            if preferences:
                remembered = "\n".join(
                    f"• {item['name']}: "
                    f"{'ưu tiên' if item['preference'] == 'LIKE' else 'tránh gợi ý'}"
                    for item in preferences
                )
                self._append_message(
                    "assistant",
                    "Ghi nhớ sản phẩm của hồ sơ này:\n"
                    + remembered
                    + "\nCó thể nói “xóa ghi nhớ [tên sản phẩm]” để quên.",
                )
                return
        self._append_message(
            "assistant",
            "Đã đổi hồ sơ; thông tin hội thoại trước đó được xóa để tránh trộn "
            "nhu cầu của hai bé. Hãy mô tả lại yêu cầu nếu cần.",
        )

    def send_message(self) -> None:
        text = self.message.text().strip()
        if not text:
            return
        self.message.clear()
        self._append_message("user", text)
        self.product_table.setRowCount(0)
        self.results = []
        self.response_detail.clear()
        self._set_actions_enabled(False)
        try:
            self._respond(text)
        except (sqlite3.Error, ValueError, PermissionError) as error:
            self._append_message(
                "assistant",
                f"Không thể xử lý yêu cầu từ dữ liệu hiện có: {error}",
            )

    def _respond(self, text: str) -> None:
        products = [
            dict(row) for row in self.database.list_recommendation_products()
        ]
        facts = extract_message_facts(text, self._known_breeds(products))
        explicit_intent = bool(facts.get("intent_explicit"))
        facts.pop("intent_explicit", None)
        urgent = bool(facts.pop("urgent_health", False))
        health_concern = bool(facts.pop("health_concern", False))
        intent = str(facts.pop("intent", "RECOMMEND"))

        for key in (
            "species",
            "breed",
            "gender",
            "birth_date",
            "weight",
            "allergies",
            "minimum_price",
            "maximum_price",
            "purpose",
        ):
            if key in facts:
                self.context[key] = facts[key]
        if "needs" in facts:
            self.context["needs"] = set(self.context.get("needs", set())) | facts["needs"]
        if explicit_intent:
            self.context["intent"] = intent
        elif intent == "CARE":
            self.context["intent"] = intent
        active_intent = str(self.context.get("intent", "RECOMMEND"))

        if urgent:
            self._append_message(
                "assistant",
                "Đây có thể là tình huống khẩn cấp. Mình không thể chẩn đoán hoặc "
                "đề xuất thuốc; hãy liên hệ bác sĩ thú y/cơ sở cấp cứu thú y ngay. "
                "Không chờ gợi ý sản phẩm.",
            )
            return
        if health_concern:
            self._append_message(
                "assistant",
                "Mình ghi nhận bé có dấu hiệu cần lưu ý. Mình không thể xác định "
                "nguyên nhân hoặc đề xuất sản phẩm để xử lý triệu chứng. Nếu bé "
                "biếng ăn/bỏ ăn, nôn, tiêu chảy, đau hoặc tình trạng kéo dài/nặng "
                "lên, hãy liên hệ bác sĩ thú y; không tự dùng thuốc hay thực phẩm "
                "bổ sung.",
            )
            return
        if active_intent == "CARE":
            self._respond_care(text)
            return
        if active_intent == "ORDER":
            self._respond_order(text)
            return
        if active_intent == "STOCK":
            self._respond_stock(text)
            return
        if active_intent in {"PET_MEMORY", "PET_MEMORY_CLEAR"}:
            self._respond_pet_memory(
                text,
                products,
                clear=active_intent == "PET_MEMORY_CLEAR",
            )
            return

        pet = self._current_pet()
        if pet is None:
            self._append_message(
                "assistant",
                "Mình cần biết loài để không gợi ý nhầm. Bé là chó, mèo, thỏ, "
                "hamster, chim hay loài nào khác?",
            )
            return

        profile_summary = self._profile_summary(pet)
        if active_intent in {"REPURCHASE", "REPLENISHMENT"}:
            self._respond_repurchase(
                pet,
                profile_summary,
                products,
                predict_due=active_intent == "REPLENISHMENT",
            )
            return

        preferences = (
            self.database.list_animal_product_preferences(self.saved_animal_id)
            if self.saved_animal_id is not None
            else []
        )
        interactions = (
            self.database.list_recommendation_interactions(self.saved_animal_id)
            if self.saved_animal_id is not None
            else []
        )
        peers = (
            self.database.list_recommendation_peer_interactions(self.saved_animal_id)
            if self.saved_animal_id is not None
            else []
        )
        self.results = recommend_products(
            products,
            pet,
            interactions,
            set(self.context.get("needs", set())),
            self.context.get("purpose"),
            self.context.get("minimum_price"),
            self.context.get("maximum_price"),
            collaborative_interactions=peers,
            product_preferences=preferences,
        )

        is_combo = active_intent == "COMBO"
        shown = (
            build_budget_combo(self.results, self.context.get("maximum_price"))
            if is_combo
            else self.results[:10]
        )
        self.results = shown
        if not shown:
            self._append_message(
                "assistant",
                f"{profile_summary}\nChưa tìm thấy sản phẩm được cấu hình phù hợp "
                "và còn tồn dùng được. Nhân viên có thể cấu hình thẻ sản phẩm hoặc "
                "nhập thêm hàng trong mục Tồn kho.",
            )
            return
        intro = (
            f"Đây là combo gợi ý cho {profile_summary}."
            if is_combo
            else f"Mình phân tích hồ sơ: {profile_summary}."
        )
        if "breed" not in self.context or "birth_date" not in self.context:
            intro += (
                "\nGợi ý hiện ở mức loài; bạn có thể trả lời thêm giống và tuổi để "
                "cá nhân hóa chính xác hơn."
            )
        if is_combo and self.context.get("maximum_price") is not None:
            total = sum(item["recommendation_price"] for item in shown)
            intro += f"\nTổng combo {total:,.0f} ₫, không vượt ngân sách đã nêu."
        self._append_message("assistant", intro)
        self._show_products(shown)

    def _profile_summary(self, pet: dict[str, Any]) -> str:
        facts = [str(pet.get("species", "chưa rõ loài"))]
        if pet.get("breed"):
            facts.append(str(pet["breed"]))
        if pet.get("birth_date"):
            from app.modules.recommendations.engine import age_group

            facts.append(f"nhóm tuổi {age_group(str(pet['birth_date']))}")
        if pet.get("weight") is not None:
            facts.append(f"{float(pet['weight']):g} kg")
        if pet.get("gender"):
            facts.append(str(pet["gender"]))
        needs = sorted(self.context.get("needs", set()))
        if needs:
            facts.append("nhu cầu: " + ", ".join(needs))
        if self.context.get("maximum_price") is not None:
            facts.append(f"ngân sách tối đa {self.context['maximum_price']:,.0f} ₫")
        return " · ".join(facts)

    def _show_products(self, products: list[dict[str, Any]]) -> None:
        self.product_table.setRowCount(len(products))
        for row, product in enumerate(products):
            set_cell(self.product_table, row, 0, product["name"])
            self.product_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, product["item_id"]
            )
            set_cell(
                self.product_table,
                row,
                1,
                RECOMMENDATION_CATEGORY_LABELS[product["recommendation_category"]],
            )
            set_cell(self.product_table, row, 2, f"{product['score']:.1f}%")
            explanations = list(product["reasons"])
            graph_paths = product.get("knowledge_paths", [])
            if graph_paths:
                explanations.append(
                    "Đồ thị tri thức: "
                    + ", ".join(path["label"] for path in graph_paths)
                )
            set_cell(self.product_table, row, 3, " · ".join(explanations))
            set_cell(
                self.product_table, row, 4, f"{product['recommendation_price']:,.0f} ₫"
            )
            set_cell(
                self.product_table,
                row,
                5,
                f"{product['usable_quantity']:g} {product['unit']}",
            )
        if products:
            self.product_table.selectRow(0)
        self._selection_changed()

    def _respond_care(self, text: str) -> None:
        normalized = normalize_message_text(text)
        if any(
            normalize_message_text(term) in normalized
            for term in ("tam bao lau", "tan suat tam", "tam cho")
        ):
            answer = (
                "Tần suất tắm phụ thuộc loài, loại lông, da và sức khỏe; không có "
                "một lịch cố định phù hợp mọi bé. Dùng sản phẩm đúng loài, tránh "
                "để nước/dầu gội vào mắt tai và hỏi bác sĩ thú y hoặc groomer nếu "
                "bé có bệnh da, ngứa hay kích ứng."
            )
        elif "vaccine" in normalized or "tiem phong" in normalized:
            answer = (
                "Lịch vaccine phụ thuộc loài, tuổi, tiền sử tiêm và nguy cơ phơi "
                "nhiễm. Hãy kiểm tra sổ tiêm và nhờ bác sĩ thú y lập lịch cho bé; "
                "mình không tự chỉ định vaccine."
            )
        elif re.search(r"\b(an|an uong|thuc an|khau phan)\b", normalized):
            answer = (
                "Chọn khẩu phần ghi rõ phù hợp loài và giai đoạn tuổi, chuyển thức "
                "ăn từ từ và luôn có nước sạch. Nếu bé bỏ ăn, nôn, tiêu chảy hoặc "
                "sụt cân, hãy hỏi bác sĩ thú y thay vì tự đổi thực phẩm bổ sung."
            )
        else:
            answer = (
                "Mình có thể hỗ trợ hướng dẫn chăm sóc chung và lịch tác vụ. "
                "Hãy cho biết bạn muốn hỏi về tắm, ăn uống, vaccine hay công việc "
                "chăm sóc cụ thể. Tình trạng bệnh cần bác sĩ thú y đánh giá."
            )
        tasks = []
        selected_id = self.saved_pet.currentData()
        actor_id = self.database.actor_id
        can_view_care = actor_id is None or self.database.has_permission(
            actor_id, "care.view"
        )
        if selected_id is not None and can_view_care:
            today = date.today().isoformat()
            tasks = [
                task
                for task in self.database.list_care_tasks()
                if task["animal_id"] == selected_id
                and not task["is_completed"]
                and str(task["scheduled_at"])[:10] >= today
            ][:5]
        if tasks:
            answer += "\n\nLịch chăm sóc sắp tới đã ghi nhận:"
            for task in tasks:
                answer += f"\n• {task['scheduled_at']}: {task['title']}"
        if self.saved_pet.currentData() is None:
            answer += (
                "\n\nChọn hồ sơ thú cưng ở phía trên nếu muốn xem lịch hiện có "
                "hoặc tạo một tác vụ chăm sóc."
            )
        self._append_message("assistant", answer)

    def _respond_stock(self, text: str) -> None:
        normalized = normalize_message_text(text)
        items = self.database.list_inventory_items()
        matches = []
        for item in items:
            name = normalize_message_text(str(item["name"]))
            code = normalize_message_text(str(item["item_code"]))
            if (name and name in normalized) or (code and code in normalized):
                matches.append(item)
        if not matches:
            self._append_message(
                "assistant",
                "Mình chưa xác định được tên hoặc mã sản phẩm trong danh mục tồn kho. "
                "Bạn gửi đúng tên/mã hàng nhé; số lượng và hạn dùng sẽ lấy trực tiếp "
                "từ cơ sở dữ liệu cửa hàng.",
            )
            return
        answer = []
        for item in matches[:5]:
            answer.append(
                f"• {item['name']} ({item['item_code']}): "
                f"{item['usable_quantity']:g} {item['unit']} còn sử dụng được; "
                f"{item['expired_quantity']:g} {item['unit']} đã hết hạn. "
                f"{'Đang kinh doanh' if item['is_active'] else 'Đã ngừng hoạt động'}."
            )
        self._append_message("assistant", "\n".join(answer))

    def _respond_pet_memory(
        self,
        text: str,
        products: list[dict[str, Any]],
        clear: bool = False,
    ) -> None:
        pet = self._current_pet()
        if pet is None or self.saved_animal_id is None:
            self._append_message(
                "assistant",
                "Để ghi nhớ sở thích lâu dài, hãy chọn hồ sơ thú cưng trong danh "
                "sách trước. Thông tin mô tả trong chat chưa được lưu thành hồ sơ.",
            )
            return
        normalized = normalize_message_text(text)
        matched_products = [
            product
            for product in products
            if normalize_message_text(str(product["name"])) in normalized
            or normalize_message_text(str(product["item_code"])) in normalized
        ]
        if len(matched_products) != 1:
            self._append_message(
                "assistant",
                "Mình chỉ có thể lưu hoặc xóa ghi nhớ cho một sản phẩm đang được "
                "cấu hình. Hãy nhắc đúng tên hoặc mã một sản phẩm trong danh mục; "
                "mình chưa tự suy diễn sở thích nguyên liệu như “cá” hay “gà”.",
            )
            return
        product = matched_products[0]
        if clear:
            answer = QMessageBox.question(
                self,
                "Xác nhận xóa ghi nhớ",
                f"Xóa ghi nhớ sở thích của bé với “{product['name']}”?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self._append_message("assistant", "Mình chưa xóa ghi nhớ.")
                return
            self.database.delete_animal_product_preference(
                self.saved_animal_id, int(product["item_id"])
            )
            self._append_message(
                "assistant",
                f"Đã xóa ghi nhớ sở thích với “{product['name']}”.",
            )
            return
        preference = "AVOID" if any(
            phrase in normalized
            for phrase in ("khong thich", "khong hop", "khong mua nua")
        ) else "LIKE"
        verb = "tránh gợi ý" if preference == "AVOID" else "ưu tiên gợi ý"
        answer = QMessageBox.question(
            self,
            "Xác nhận ghi nhớ sở thích",
            f"Lưu rằng bé {pet.get('name', 'này')} muốn {verb} "
            f"“{product['name']}” cho các lần tư vấn sau?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self._append_message("assistant", "Mình chưa lưu thay đổi sở thích.")
            return
        self.database.save_animal_product_preference(
            self.saved_animal_id,
            int(product["item_id"]),
            preference,
            "Được nhân viên xác nhận từ yêu cầu trong Advisor.",
        )
        self._append_message(
            "assistant",
            f"Đã lưu sở thích của bé: {verb} “{product['name']}”. "
            "Ghi nhớ này chỉ áp dụng cho đúng sản phẩm, không suy rộng sang "
            "nhãn hiệu/nguyên liệu khác.",
        )

    def _respond_repurchase(
        self,
        pet: dict[str, Any],
        summary: str,
        products: list[dict[str, Any]],
        predict_due: bool = False,
    ) -> None:
        if self.saved_animal_id is None:
            self._append_message(
                "assistant",
                "Để tìm món bé từng mua, hãy chọn hồ sơ bé đã gắn với lịch sử tương tác. "
                "Hồ sơ mô tả trong chat chưa có lịch sử lưu.",
            )
            return
        interactions = self.database.list_recommendation_interactions(
            self.saved_animal_id
        )
        preferences = self.database.list_animal_product_preferences(
            self.saved_animal_id
        )
        predictions = predict_replenishments(interactions)
        product_by_id = {int(item["item_id"]): item for item in products}
        due_lines = []
        for prediction in predictions:
            product = product_by_id.get(prediction["item_id"])
            if product is None:
                continue
            due_date = prediction["predicted_date"].strftime("%d/%m/%Y")
            stock_note = (
                f"còn {product['usable_quantity']:g} {product['unit']}"
                if product["usable_quantity"] > 0
                else "hiện không có tồn dùng được"
            )
            due_lines.append(
                f"• {product['name']}: chu kỳ ghi nhận thường khoảng "
                f"{prediction['typical_interval_days']} ngày; lần gần nhất "
                f"{prediction['last_purchase_date']:%d/%m/%Y}; lần tiếp theo "
                f"ước tính {due_date} ({stock_note})."
            )
        purchases = {
            int(event["item_id"])
            for event in interactions
            if event["event_type"] == "PURCHASE"
        }
        ranked = recommend_products(
            products,
            pet,
            interactions,
            set(self.context.get("needs", set())),
            self.context.get("purpose"),
            self.context.get("minimum_price"),
            self.context.get("maximum_price"),
            collaborative_interactions=self.database.list_recommendation_peer_interactions(
                self.saved_animal_id
            ),
            product_preferences=preferences,
        )
        self.results = [item for item in ranked if int(item["item_id"]) in purchases]
        if not self.results:
            if predict_due and due_lines:
                self._append_message(
                    "assistant",
                    "Ước tính chu kỳ mua lại từ các lần nhân viên ghi nhận "
                    "“Đã mua” trong Advisor:\n"
                    + "\n".join(due_lines)
                    + "\nĐây không phải lịch sử hóa đơn và chỉ là tham khảo.",
                )
                return
            self._append_message(
                "assistant",
                f"Mình chưa thấy sản phẩm đã mua còn hàng dùng được cho {summary}. "
                "Lịch sử chỉ chứa các lần mua đã ghi nhận trong Advisor, không phải "
                "hóa đơn bán hàng.",
            )
            return
        lead = (
            "Dự đoán mua lại dựa trên các lần nhân viên ghi nhận trong Advisor "
            "(không phải hóa đơn):\n"
            + "\n".join(due_lines)
            + "\n\n"
            if predict_due and due_lines
            else ""
        )
        self._append_message(
            "assistant",
            lead
            + f"Các sản phẩm đã ghi nhận mua, hiện còn tồn dùng được cho {summary}:",
        )
        self._show_products(self.results)

    def _respond_order(self, text: str) -> None:
        actor_id = self.database.actor_id
        if actor_id is not None and not self.database.has_permission(actor_id, "sales.view"):
            self._append_message(
                "assistant",
                "Tài khoản hiện tại không có quyền xem đơn bán. Hãy chuyển yêu cầu "
                "cho nhân viên bán hàng.",
            )
            return
        code = extract_order_code(text)
        if code is None:
            self._append_message(
                "assistant",
                "Bạn gửi mã đơn hàng để mình tra trạng thái thanh toán trong hệ thống. "
                "Ứng dụng hiện quản lý đơn bán thú cưng; chưa có trạng thái giao vận, "
                "đổi trả hoặc tracking hãng vận chuyển.",
            )
            return
        code = code.casefold()
        orders = [
            order
            for order in self.database.list_sales_orders()
            if str(order["order_code"]).casefold() == code
        ]
        if not orders:
            self._append_message("assistant", "Không tìm thấy mã đơn trong dữ liệu cửa hàng.")
            return
        order = orders[0]
        balance = max(0.0, float(order["total_amount"]) - float(order["paid_amount"]))
        items = self.database.list_order_items(order["id"])
        names = ", ".join(item["animal_name"] for item in items)
        self._append_message(
            "assistant",
            f"Đơn {order['order_code']} của {order['customer_name']}: "
            f"{ORDER_STATUS_LABELS.get(order['status'], order['status'])}; "
            f"tổng {order['total_amount']:,.0f} ₫, đã thu {order['paid_amount']:,.0f} ₫, "
            f"còn {balance:,.0f} ₫. Hồ sơ: {names or 'không có'}.\n"
            "Dữ liệu này không bao gồm tình trạng giao hàng.",
        )

    def _selection_changed(self, *_: Any) -> None:
        row = self.product_table.currentRow()
        product = next(
            (
                candidate
                for candidate in self.results
                if row >= 0
                and self.product_table.item(row, 0) is not None
                and candidate["item_id"]
                == self.product_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            ),
            None,
        )
        self._set_actions_enabled(
            product is not None and self.saved_animal_id is not None
        )
        if product is None:
            self.response_detail.clear()
            return
        breakdown = product["score_breakdown"]
        self.response_detail.setText(
            f"{product['name']}: {product['score']:.1f}% phù hợp. "
            f"Loài {breakdown['species']:.0f}, tuổi {breakdown['age']:.0f}, "
            f"giống/giới tính {breakdown['breed']:.0f}, nhu cầu {breakdown['needs']:.0f}, "
            f"hành vi {breakdown['behavior']:.0f}, lịch sử mua "
            f"{breakdown['purchase_history']:.0f}, phổ biến {breakdown['popularity']:.0f}, "
            f"tồn {breakdown['stock']:.0f}."
        )

    def _set_actions_enabled(self, enabled: bool) -> None:
        for button in self.action_buttons:
            button.setEnabled(enabled)

    def record_event(self, event_type: str) -> None:
        if self.saved_animal_id is None:
            return
        row = self.product_table.currentRow()
        if row < 0 or self.product_table.item(row, 0) is None:
            return
        item_id = self.product_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if event_type == "PURCHASE":
            answer = QMessageBox.question(
                self,
                "Ghi nhận lịch sử mua",
                "Chỉ lưu hành vi để cá nhân hóa; không tạo đơn và không trừ kho. Tiếp tục?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            self.database.record_recommendation_interaction(
                self.saved_animal_id, item_id, event_type
            )
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể ghi hành vi", str(error))
            return
        self._append_message(
            "assistant", f"Đã ghi nhận: {RECOMMENDATION_EVENT_LABELS[event_type]}."
        )

    def create_care_task(self) -> None:
        animals = self.database.list_animals()
        if not animals:
            QMessageBox.information(
                self, "Chưa có thú cưng", "Tạo hồ sơ thú cưng trước khi lập lịch."
            )
            return
        dialog = CareTaskDialog(self, animals)
        selected_id = self.saved_pet.currentData()
        if selected_id is not None:
            index = dialog.animal.findData(selected_id)
            if index >= 0:
                dialog.animal.setCurrentIndex(index)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.database.add_care_task(dialog.values())
        except (sqlite3.Error, ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Không thể tạo lịch", str(error))
            return
        self._append_message(
            "assistant",
            "Đã tạo lịch chăm sóc theo thông tin bạn xác nhận trong biểu mẫu.",
        )
