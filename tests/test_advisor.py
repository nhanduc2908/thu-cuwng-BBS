from datetime import date

import pytest

from app.modules.recommendations.advisor import (
    build_budget_combo,
    extract_message_facts,
    extract_order_code,
    predict_replenishments,
)


def test_advisor_extracts_vietnamese_pet_facts_without_misreading_age_as_budget():
    facts = extract_message_facts(
        "Bé là chó Corgi cái, 4 tháng tuổi, 6 kg, da nhạy cảm; "
        "ngân sách dưới 500k, tìm thức ăn"
    )

    assert facts["species"] == "cho"
    assert facts["breed"] == "corgi"
    assert facts["age_months"] == 4
    assert facts["weight"] == 6
    assert facts["gender"] == "Cái"
    assert facts["needs"] == {"sensitive_skin"}
    assert facts["minimum_price"] == 0
    assert facts["maximum_price"] == 500_000
    assert facts["purpose"] == "FOOD"
    assert facts["intent"] == "RECOMMEND"


def test_advisor_extracts_ranges_allergies_and_health_safety_flags():
    facts = extract_message_facts(
        "Mèo dị ứng gà, tìm đồ ăn từ 100.000 đến 300.000 đồng"
    )

    assert facts["species"] == "meo"
    assert facts["allergies"] == {"chicken"}
    assert facts["minimum_price"] == 100_000
    assert facts["maximum_price"] == 300_000

    urgent = extract_message_facts("Bé đang khó thở")
    assert urgent["urgent_health"] is True
    assert urgent["health_concern"] is True

    non_urgent = extract_message_facts("Bé biếng ăn")
    assert non_urgent["urgent_health"] is False
    assert non_urgent["health_concern"] is True


def test_advisor_keeps_intent_explicit_only_for_direct_requests():
    assert extract_message_facts("Tạo combo cho chó")["intent_explicit"] is True
    follow_up = extract_message_facts("Corgi 4 tháng")
    assert follow_up["intent"] == "RECOMMEND"
    assert follow_up["intent_explicit"] is False


def test_replenishment_prediction_uses_distinct_purchase_days_and_horizon():
    events = [
        {"item_id": 7, "event_type": "PURCHASE", "occurred_at": "2026-07-01 09:00:00"},
        {"item_id": 7, "event_type": "PURCHASE", "occurred_at": "2026-07-01 16:00:00"},
        {"item_id": 7, "event_type": "PURCHASE", "occurred_at": "2026-07-29 09:00:00"},
        {"item_id": 7, "event_type": "PURCHASE", "occurred_at": "2026-08-26 09:00:00"},
        {"item_id": 7, "event_type": "VIEW", "occurred_at": "2026-09-01 09:00:00"},
        {"item_id": 8, "event_type": "PURCHASE", "occurred_at": "2026-08-01 09:00:00"},
        {"item_id": 8, "event_type": "PURCHASE", "occurred_at": "2026-08-29 09:00:00"},
    ]

    predictions = predict_replenishments(events, today=date(2026, 9, 21))

    assert len(predictions) == 1
    assert predictions[0]["item_id"] == 7
    assert predictions[0]["predicted_date"] == date(2026, 9, 23)
    assert predictions[0]["typical_interval_days"] == 28
    assert predictions[0]["purchase_count"] == 3
    assert predictions[0]["days_until"] == 2


def test_replenishment_prediction_rejects_invalid_horizon_and_history():
    with pytest.raises(ValueError):
        predict_replenishments([], horizon_days=-1)
    with pytest.raises(ValueError):
        predict_replenishments(
            [{"item_id": 1, "event_type": "PURCHASE", "occurred_at": "unknown"}]
        )


def test_replenishment_request_has_a_distinct_explicit_intent():
    facts = extract_message_facts("Thức ăn của bé sắp hết rồi")

    assert facts["intent"] == "REPLENISHMENT"
    assert facts["intent_explicit"] is True


def test_product_memory_requests_and_forget_requests_have_separate_intents():
    assert extract_message_facts(
        "Mochi không thích Thức ăn mèo"
    )["intent"] == "PET_MEMORY"
    assert extract_message_facts(
        "Xóa ghi nhớ Thức ăn mèo"
    )["intent"] == "PET_MEMORY_CLEAR"
    symptom = extract_message_facts("Mochi không ăn từ hôm qua")
    assert symptom["intent"] != "PET_MEMORY"
    assert symptom["health_concern"] is True


def test_unknown_breed_does_not_replace_a_saved_species_with_blank_text():
    facts = extract_message_facts("Giống Turkish Van", {"turkish van"})

    assert facts["breed"] == "turkish_van"
    assert "species" not in facts


def test_combo_respects_budget_and_category_priority():
    ranked = [
        {"item_id": 1, "recommendation_category": "FOOD", "recommendation_price": 260_000, "score": 95},
        {"item_id": 2, "recommendation_category": "HYGIENE", "recommendation_price": 40_000, "score": 85},
        {"item_id": 3, "recommendation_category": "ACCESSORY", "recommendation_price": 50_000, "score": 80},
        {"item_id": 4, "recommendation_category": "SUPPLEMENT", "recommendation_price": 1, "score": 10},
    ]

    combo = build_budget_combo(ranked, 350_000)

    assert [item["item_id"] for item in combo] == [1, 2, 3]
    assert sum(item["recommendation_price"] for item in combo) <= 350_000


def test_combo_optimizer_prefers_more_relevant_categories_over_greedy_food_pick():
    ranked = [
        {"item_id": 1, "recommendation_category": "FOOD", "recommendation_price": 280_000, "score": 99},
        {"item_id": 2, "recommendation_category": "HYGIENE", "recommendation_price": 100_000, "score": 80},
        {"item_id": 3, "recommendation_category": "ACCESSORY", "recommendation_price": 100_000, "score": 80},
    ]

    combo = build_budget_combo(ranked, 300_000)

    assert [item["item_id"] for item in combo] == [2, 3]
    assert sum(item["recommendation_price"] for item in combo) <= 300_000


def test_unbudgeted_combo_uses_best_ranked_item_per_category():
    ranked = [
        {"item_id": 1, "recommendation_category": "FOOD", "recommendation_price": 250_000, "score": 75},
        {"item_id": 2, "recommendation_category": "FOOD", "recommendation_price": 200_000, "score": 90},
        {"item_id": 3, "recommendation_category": "HYGIENE", "recommendation_price": 50_000, "score": 80},
    ]

    combo = build_budget_combo(ranked, None)

    assert [item["item_id"] for item in combo] == [2, 3]


def test_order_code_parser_accepts_contextual_and_standalone_codes():
    assert extract_order_code("Tra mã đơn: PET-2026-001") == "PET-2026-001"
    assert extract_order_code("DH2026001") == "DH2026001"
    assert extract_order_code("Cho tôi biết đơn hàng nào") is None
