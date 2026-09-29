from datetime import date, timedelta

from app.modules.recommendations.engine import recommend_products


def product(**overrides):
    value = {
        "item_id": 1,
        "name": "Thức ăn cho chó con",
        "recommendation_category": "FOOD",
        "species_tags": '["cho"]',
        "age_groups": '["young"]',
        "breed_tags": "[]",
        "gender_tags": "[]",
        "needs_tags": '["digestion"]',
        "health_tags": "[]",
        "activity_tags": "[]",
        "coat_tags": "[]",
        "environment_tags": "[]",
        "avoid_tags": "[]",
        "minimum_weight": None,
        "maximum_weight": None,
        "recommendation_price": 250_000,
        "popularity": 80,
        "usable_quantity": 5,
        "unit": "gói",
    }
    value.update(overrides)
    return value


def pet(**overrides):
    value = {
        "species": "Chó",
        "breed": "Corgi",
        "gender": "Đực",
        "birth_date": (date.today() - timedelta(days=180)).isoformat(),
        "weight": 8.0,
        "allergies": "",
        "health_status": "Bình thường",
        "exercise_needs": "",
        "behavior": "",
    }
    value.update(overrides)
    return value


def test_recommendation_filters_species_age_budget_stock_and_veterinary():
    candidates = [
        product(),
        product(item_id=2, name="Thức ăn mèo", species_tags='["meo"]'),
        product(item_id=3, name="Hết hàng", usable_quantity=0),
        product(
            item_id=4,
            name="Thuốc",
            recommendation_category="VETERINARY",
        ),
        product(item_id=5, name="Senior", age_groups='["senior"]'),
        product(item_id=6, name="Ngoài ngân sách", recommendation_price=400_000),
    ]

    results = recommend_products(
        candidates,
        pet(),
        selected_needs={"digestion"},
        minimum_price=0,
        maximum_price=300_000,
    )

    assert [result["item_id"] for result in results] == [1, 5]
    assert results[0]["score"] > 70
    assert results[0]["score_breakdown"]["stock"] == 100
    assert results[0]["score"] > results[1]["score"]


def test_recommendation_excludes_allergy_conflicts_and_weight_mismatch():
    candidates = [
        product(avoid_tags='["chicken"]'),
        product(item_id=2, name="Cân nặng không phù hợp", minimum_weight=15),
    ]

    results = recommend_products(
        candidates,
        pet(allergies="chicken", weight=8),
    )

    assert results == []


def test_recommendation_filters_exact_age_bounds_in_months_and_years():
    too_old = product(age_min_months=18, age_max_months=24)
    year_bands = product(
        item_id=2,
        age_min_months=1,
        age_max_months=2,
        age_unit="YEAR",
    )

    results = recommend_products(
        [too_old, year_bands],
        pet(birth_date=(date.today() - timedelta(days=400)).isoformat()),
    )

    assert [result["item_id"] for result in results] == [2]


def test_recommendation_scores_behavior_and_purchase_history():
    candidate = product(item_id=1, needs_tags='["digestion"]')
    related = product(
        item_id=2,
        name="Men tiêu hóa",
        recommendation_category="SUPPLEMENT",
        needs_tags='["digestion"]',
    )
    interaction = {
        "item_id": 2,
        "event_type": "PURCHASE",
        "purpose_tags": '["supplement"]',
        "needs_tags": '["digestion"]',
        "health_tags": "[]",
        "activity_tags": "[]",
        "coat_tags": "[]",
        "environment_tags": "[]",
    }
    baseline = recommend_products([candidate], pet())[0]
    personalized = recommend_products(
        [candidate, related],
        pet(),
        interactions=[interaction],
    )

    assert personalized[0]["item_id"] == 2
    assert personalized[0]["score_breakdown"]["purchase_history"] > 50
    assert baseline["score_breakdown"]["behavior"] == 50


def test_recommendation_uses_anonymized_item_to_item_peer_signals():
    candidate = product(item_id=3, needs_tags='["training"]')
    owned_history = [
        {
            "item_id": 2,
            "event_type": "CLICK",
        }
    ]
    peer_history = [
        {
            "peer_animal_id": 10,
            "anchor_item_id": 2,
            "item_id": 3,
            "event_type": "PURCHASE",
        },
        {
            "peer_animal_id": 11,
            "anchor_item_id": 2,
            "item_id": 3,
            "event_type": "LIKE",
        },
    ]

    result = recommend_products(
        [candidate],
        pet(),
        interactions=owned_history,
        collaborative_interactions=peer_history,
    )[0]

    assert result["score_breakdown"]["behavior"] > 50


def test_recommendation_uses_breed_and_gender_and_reports_match_reasons():
    candidate = product(breed_tags='["corgi"]', gender_tags='["đực"]')

    result = recommend_products([candidate], pet())[0]

    assert result["score_breakdown"]["breed"] == 100
    assert "Phù hợp giống" in result["reasons"]


def test_recommendation_includes_only_explicit_knowledge_graph_paths():
    candidate = product(
        species_tags='["cho"]',
        age_groups='["young"]',
        breed_tags='["corgi"]',
        gender_tags='["duc"]',
        needs_tags='["digestion"]',
    )
    current_pet = pet(exercise_needs="digestion")

    result = recommend_products([candidate], current_pet)[0]

    relations = {path["relation"] for path in result["knowledge_paths"]}
    assert relations == {"SPECIES", "AGE", "BREED", "GENDER", "NEED"}
    assert all(path["pet_value"] == path["product_value"] for path in result["knowledge_paths"])


def test_knowledge_graph_does_not_claim_unconfigured_breed_or_need_matches():
    candidate = product(breed_tags="[]", needs_tags="[]")

    result = recommend_products(
        [candidate],
        pet(exercise_needs="digestion"),
        selected_needs={"digestion"},
    )[0]

    relations = {path["relation"] for path in result["knowledge_paths"]}
    assert "SPECIES" in relations
    assert "BREED" not in relations
    assert "NEED" not in relations


def test_knowledge_graph_links_health_only_when_product_explicitly_tags_it():
    candidate = product(health_tags='["theo_doi"]')

    result = recommend_products(
        [candidate],
        pet(health_status="Theo dõi"),
    )[0]

    health_paths = [
        path for path in result["knowledge_paths"] if path["relation"] == "HEALTH"
    ]
    assert len(health_paths) == 1
    assert "đã cấu hình" in health_paths[0]["label"]
