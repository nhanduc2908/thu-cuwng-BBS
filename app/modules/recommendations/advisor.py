from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
from statistics import median
import re
import unicodedata
from typing import Any

from app.modules.recommendations.engine import normalize_tag


BREED_SPECIES = {
    "akita": "cho",
    "alaskan_malamute": "cho",
    "american_bulldog": "cho",
    "american_shorthair": "meo",
    "basset_hound": "cho",
    "beagle": "cho",
    "bengal": "meo",
    "bernese_mountain_dog": "cho",
    "bichon": "cho",
    "bichon_frise": "cho",
    "border_collie": "cho",
    "british_shorthair": "meo",
    "bulldog": "cho",
    "cavalier_king_charles_spaniel": "cho",
    "chihuahua": "cho",
    "corgi": "cho",
    "dachshund": "cho",
    "doberman": "cho",
    "french_bulldog": "cho",
    "german_shepherd": "cho",
    "golden_retriever": "cho",
    "great_dane": "cho",
    "husky": "cho",
    "jack_russell_terrier": "cho",
    "labrador": "cho",
    "labrador_retriever": "cho",
    "maine_coon": "meo",
    "malinois": "cho",
    "miniature_poodle": "cho",
    "pomeranian": "cho",
    "poodle": "cho",
    "ragdoll": "meo",
    "rottweiler": "cho",
    "samoyed": "cho",
    "scottish_fold": "meo",
    "shiba_inu": "cho",
    "siamese": "meo",
    "siberian_husky": "cho",
    "sphynx": "meo",
    "toy_poodle": "cho",
    "yorkshire_terrier": "cho",
}

SPECIES_ALIASES = {
    "cho": "cho",
    "cho_con": "cho",
    "dog": "cho",
    "dogs": "cho",
    "chon": "cho",
    "meo": "meo",
    "meo_con": "meo",
    "cat": "meo",
    "cats": "meo",
    "tho": "tho",
    "rabbit": "tho",
    "hamster": "hamster",
    "chuot_lang": "guinea_pig",
    "guinea_pig": "guinea_pig",
    "chim": "chim",
    "bird": "chim",
    "bo_sat": "bo_sat",
    "reptile": "bo_sat",
    "rua": "rua",
    "nhim": "nhim",
}

NEED_PHRASES = {
    "shedding": ("rụng lông", "rụng lông nhiều", "shedding"),
    "long_coat": ("lông dài", "long coat"),
    "sensitive_skin": ("da nhạy cảm", "da de kich ung", "sensitive skin"),
    "low_activity": ("ít vận động", "van dong it", "ít chạy", "low activity"),
    "high_activity": ("hiếu động", "hoạt động nhiều", "high activity"),
    "digestion": ("tiêu hóa nhạy cảm", "hay roi loan tieu hoa", "digestion"),
    "weight_control": ("kiểm soát cân nặng", "thừa cân", "weight control"),
    "dental_care": ("chăm sóc răng", "hôi miệng", "dental"),
    "training": ("huấn luyện", "đang tập", "training"),
    "indoor": ("nuôi trong nhà", "ở trong nhà", "indoor"),
    "outdoor": ("hay ra ngoài", "đi dạo ngoài trời", "outdoor"),
    "poor_appetite": ("biếng ăn", "kén ăn", "bỏ ăn", "poor appetite"),
}

PURPOSE_PHRASES = {
    "FOOD": ("thức ăn", "đồ ăn", "pate", "hạt", "food", "ăn uống"),
    "HYGIENE": ("vệ sinh", "tắm", "cát vệ sinh", "lông", "grooming"),
    "ACCESSORY": ("phụ kiện", "dây dắt", "balo", "vòng cổ", "accessory"),
    "SUPPLEMENT": ("bổ sung", "vitamin", "probiotic", "thực phẩm bổ sung"),
    "TRAINING": ("huấn luyện", "đồ chơi", "đồ gặm", "training", "toy"),
}

URGENT_HEALTH_PHRASES = (
    "kho tho",
    "co giat",
    "bat tinh",
    "ngat",
    "chay mau",
    "non lien tuc",
    "tieu chay ra mau",
)
HEALTH_CONCERN_PHRASES = (
    "bi eng an",
    "bieng an",
    "bo an",
    "khong an",
    "non",
    "tieu chay",
    "sot",
    "ngua lien tuc",
    "sut can",
    "di ung",
    "dau",
)
COMBO_CATEGORY_PRIORITY = (
    "FOOD",
    "HYGIENE",
    "ACCESSORY",
    "TRAINING",
    "OTHER",
    "SUPPLEMENT",
)


def normalize_message_text(value: str) -> str:
    value = value.casefold().replace("đ", "d")
    return "".join(
        character
        for character in unicodedata.normalize("NFD", value)
        if unicodedata.category(character) != "Mn"
    )


def _parse_money_token(token: str) -> float | None:
    match = re.fullmatch(
        r"\s*(\d[\d.,]*)\s*(k|nghin|ngan|trieu|tr|dong)?\s*",
        normalize_message_text(token).replace("₫", " dong"),
    )
    if not match:
        return None
    number, suffix = match.groups()
    digits = number.replace(".", "").replace(",", "")
    if not digits:
        return None
    amount = float(digits)
    if suffix in {"k", "nghin", "ngan"}:
        amount *= 1_000
    elif suffix in {"tr", "trieu"}:
        amount *= 1_000_000
    return amount if amount > 0 else None


def _extract_budget(text: str) -> tuple[float | None, float | None]:
    normalized = normalize_message_text(text)
    without_pet_measurements = re.sub(
        r"\b\d{1,3}(?:[.,]\d+)?\s*(?:thang(?:\s*tuoi)?|tuoi|nam(?:\s*tuoi)?|kg|ki\s*lo|ki|ky)\b",
        " ",
        normalized,
    )
    token = r"(\d[\d.,]*\s*(?:k|nghin|ngan|trieu|tr|dong|₫)?)"
    range_match = re.search(
        token + r"\s*(?:den|toi)\s*" + token,
        without_pet_measurements,
    )
    if range_match:
        first = _parse_money_token(range_match.group(1))
        second = _parse_money_token(range_match.group(2))
        if first is not None and second is not None:
            return min(first, second), max(first, second)
    amount_match = re.search(token, without_pet_measurements)
    amount = _parse_money_token(amount_match.group(1)) if amount_match else None
    if amount is None:
        return None, None
    if any(word in normalized for word in ("tren ", "hon ", "tu ")) and "duoi" not in normalized:
        return amount, None
    return 0, amount


def _subtract_months(today: date, months: int) -> date:
    month_index = today.year * 12 + today.month - 1 - months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    day = min(today.day, monthrange(year, month)[1])
    return date(year, month, day)


def build_budget_combo(
    ranked: list[dict[str, Any]], maximum_price: float | None
) -> list[dict[str, Any]]:
    if maximum_price is None:
        selected: list[dict[str, Any]] = []
        for category in COMBO_CATEGORY_PRIORITY:
            best = _best_unbudgeted_category_product(ranked, category)
            if best is not None:
                selected.append(best)
        return selected
    budget = float(maximum_price)
    states: list[tuple[float, float, tuple[dict[str, Any], ...]]] = [
        (0.0, 0.0, ())
    ]
    for category in COMBO_CATEGORY_PRIORITY:
        candidates = [
            item for item in ranked if item["recommendation_category"] == category
        ]
        expanded = []
        for spent, score, selected in states:
            for item in candidates:
                price = float(item["recommendation_price"])
                if spent + price <= budget:
                    expanded.append(
                        (
                            spent + price,
                            score + float(item.get("score", 0)),
                            (*selected, item),
                        )
                    )
            expanded.append((spent, score, selected))

        frontier: list[tuple[float, float, tuple[dict[str, Any], ...]]] = []
        best_score_by_coverage: list[float] = []
        for state in sorted(
            expanded,
            key=lambda candidate: (
                candidate[0],
                -len(candidate[2]),
                -candidate[1],
            ),
        ):
            spent, score, selected = state
            coverage = len(selected)
            if any(
                previous_coverage >= coverage
                and best_score_by_coverage[previous_coverage] >= score
                for previous_coverage in range(coverage, len(best_score_by_coverage))
            ):
                continue
            frontier.append(state)
            if coverage >= len(best_score_by_coverage):
                best_score_by_coverage.extend(
                    [-float("inf")] * (coverage - len(best_score_by_coverage) + 1)
                )
            best_score_by_coverage[coverage] = max(
                best_score_by_coverage[coverage], score
            )
        states = frontier

    best = max(
        states,
        key=lambda state: (len(state[2]), state[1], -state[0]),
    )
    return list(best[2])


def _best_unbudgeted_category_product(
    ranked: list[dict[str, Any]], category: str
) -> dict[str, Any] | None:
    candidates = [
        item for item in ranked if item["recommendation_category"] == category
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: (
            float(item.get("score", 0)),
            -float(item["recommendation_price"]),
        ),
    )


def extract_order_code(message: str) -> str | None:
    text = normalize_message_text(message).strip()
    stopwords = {"nao", "gi", "la", "chua", "co", "toi", "nay", "kia"}
    contextual_match = re.search(
        r"\b(?:ma don(?: hang)?|don hang)\s*(?:la|:)?\s*"
        r"([a-z0-9][a-z0-9_-]{2,})\b",
        text,
    )
    if contextual_match:
        code = contextual_match.group(1)
        return None if code in stopwords else code.upper()
    if re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,}", text):
        return text.upper()
    return None


def predict_replenishments(
    purchase_events: list[dict[str, Any]],
    today: date | None = None,
    horizon_days: int = 7,
) -> list[dict[str, Any]]:
    if horizon_days < 0:
        raise ValueError("Khoảng dự báo không được là số ngày âm.")
    current_date = today or date.today()
    dates_by_item: dict[int, set[date]] = {}
    for event in purchase_events:
        if event.get("event_type") != "PURCHASE":
            continue
        try:
            item_id = int(event["item_id"])
            occurred_at = datetime.fromisoformat(str(event["occurred_at"]))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Lịch sử mua sản phẩm có dữ liệu ngày hoặc mã hàng lỗi.") from error
        dates_by_item.setdefault(item_id, set()).add(occurred_at.date())

    predictions = []
    for item_id, purchase_dates in dates_by_item.items():
        ordered_dates = sorted(purchase_dates)
        if len(ordered_dates) < 3:
            continue
        intervals = [
            (later - earlier).days
            for earlier, later in zip(ordered_dates, ordered_dates[1:])
        ]
        typical_interval = int(round(median(intervals)))
        if typical_interval < 1:
            continue
        next_date = ordered_dates[-1] + timedelta(days=typical_interval)
        days_until = (next_date - current_date).days
        if days_until > horizon_days:
            continue
        predictions.append(
            {
                "item_id": item_id,
                "last_purchase_date": ordered_dates[-1],
                "predicted_date": next_date,
                "typical_interval_days": typical_interval,
                "purchase_count": len(ordered_dates),
                "days_until": days_until,
            }
        )
    return sorted(predictions, key=lambda item: item["predicted_date"])


def extract_message_facts(
    message: str,
    known_breeds: set[str] | None = None,
) -> dict[str, Any]:
    text = normalize_message_text(message)
    facts: dict[str, Any] = {}
    for phrase, species in SPECIES_ALIASES.items():
        if re.search(rf"(?<![a-z0-9_]){re.escape(phrase)}(?![a-z0-9_])", text):
            facts["species"] = species
            break

    breed_names = set(BREED_SPECIES)
    breed_names.update(normalize_tag(name) for name in (known_breeds or set()))
    for breed in sorted(breed_names, key=len, reverse=True):
        breed_pattern = r"[\s_-]+".join(
            re.escape(part) for part in breed.split("_")
        )
        if re.search(rf"(?<![a-z0-9_]){breed_pattern}(?![a-z0-9_])", text):
            facts["breed"] = breed
            inferred_species = BREED_SPECIES.get(breed)
            if inferred_species:
                facts.setdefault("species", inferred_species)
            break

    age_match = re.search(r"\b(\d{1,2})\s*(thang(?:\s*tuoi)?|tuoi|nam(?:\s*tuoi)?)\b", text)
    if age_match:
        value = int(age_match.group(1))
        unit = age_match.group(2)
        months = value if unit.startswith("thang") else value * 12
        if 0 <= months <= 480:
            facts["age_months"] = months
            facts["birth_date"] = _subtract_months(date.today(), months).isoformat()

    weight_match = re.search(r"\b(\d+(?:[.,]\d+)?)\s*(kg|ki lo|ki|ky)\b", text)
    if weight_match:
        weight = float(weight_match.group(1).replace(",", "."))
        if 0 < weight <= 100_000:
            facts["weight"] = weight

    if re.search(r"\b(cai|female)\b", text):
        facts["gender"] = "Cái"
    elif re.search(r"\b(duc|male)\b", text):
        facts["gender"] = "Đực"

    needs: set[str] = set()
    for tag, phrases in NEED_PHRASES.items():
        if any(normalize_message_text(phrase) in text for phrase in phrases):
            needs.add(tag)
    if needs:
        facts["needs"] = needs
    allergens = {
        "chicken": ("di ung ga", "khong an duoc ga", "allergic to chicken"),
        "dairy": ("di ung sua", "khong dung duoc sua"),
        "beef": ("di ung bo", "khong an duoc bo"),
        "fish": ("di ung ca", "khong an duoc ca"),
    }
    allergy_tags = {
        tag
        for tag, phrases in allergens.items()
        if any(normalize_message_text(phrase) in text for phrase in phrases)
    }
    if allergy_tags:
        facts["allergies"] = allergy_tags

    minimum_price, maximum_price = _extract_budget(message)
    if minimum_price is not None:
        facts["minimum_price"] = minimum_price
    if maximum_price is not None:
        facts["maximum_price"] = maximum_price

    for category, phrases in PURPOSE_PHRASES.items():
        if any(normalize_message_text(phrase) in text for phrase in phrases):
            facts["purpose"] = category
            break

    if any(
        phrase in text
        for phrase in (
            "xoa ghi nho",
            "bo ghi nho",
            "quen so thich",
            "xoa so thich",
        )
    ):
        facts["intent"] = "PET_MEMORY_CLEAR"
        facts["intent_explicit"] = True
    elif any(
        phrase in text
        for phrase in (
            "khong thich",
            "khong hop",
            "khong mua nua",
            "rat thich",
            "yeu thich",
            "be thich",
            "thich san pham",
        )
    ):
        facts["intent"] = "PET_MEMORY"
        facts["intent_explicit"] = True
    elif any(
        word in text
        for word in ("sap het", "gan het", "den ky mua", "chu ky mua", "mua lai")
    ):
        facts["intent"] = "REPLENISHMENT"
        facts["intent_explicit"] = True
    elif any(word in text for word in ("combo", "bo san pham", "starter kit", "goi do")):
        facts["intent"] = "COMBO"
        facts["intent_explicit"] = True
    elif any(
        word in text
        for word in (
            "tam bao lau",
            "cham soc",
            "bao lau nen",
            "nen lam gi",
            "vaccine",
            "tiem phong",
        )
    ):
        facts["intent"] = "CARE"
        facts["intent_explicit"] = True
    elif any(word in text for word in ("lan truoc", "da mua")):
        facts["intent"] = "REPURCHASE"
        facts["intent_explicit"] = True
    elif any(word in text for word in ("don hang", "ma don", "doi tra", "giao hang")):
        facts["intent"] = "ORDER"
        facts["intent_explicit"] = True
    elif any(word in text for word in ("con hang", "ton kho", "co san khong", "con khong")):
        facts["intent"] = "STOCK"
        facts["intent_explicit"] = True
    elif any(word in text for word in ("goi y", "nen mua", "tim ", "mua gi", "recommend")):
        facts["intent"] = "RECOMMEND"
        facts["intent_explicit"] = True
    else:
        facts["intent"] = "RECOMMEND"
        facts["intent_explicit"] = False

    facts["urgent_health"] = any(
        normalize_message_text(phrase) in text for phrase in URGENT_HEALTH_PHRASES
    )
    facts["health_concern"] = facts["urgent_health"] or any(
        normalize_message_text(phrase) in text for phrase in HEALTH_CONCERN_PHRASES
    )

    return facts
