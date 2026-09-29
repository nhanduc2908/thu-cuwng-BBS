from datetime import date, timedelta

import pytest

from app.modules.recommendations.evaluation import evaluate_recommendations


def evaluation_product(item_id, **overrides):
    product = {
        "item_id": item_id,
        "name": f"Food {item_id}",
        "recommendation_category": "FOOD",
        "species_tags": '["cho"]',
        "age_groups": "[]",
        "breed_tags": "[]",
        "gender_tags": "[]",
        "needs_tags": "[]",
        "health_tags": "[]",
        "activity_tags": "[]",
        "coat_tags": "[]",
        "environment_tags": "[]",
        "avoid_tags": "[]",
        "recommendation_price": 100_000,
        "popularity": 50,
        "usable_quantity": 5,
    }
    product.update(overrides)
    return product


def test_evaluation_uses_temporal_holdout_and_reports_ranking_metrics():
    products = [
        evaluation_product(1, popularity=90),
        evaluation_product(2, popularity=10, needs_tags='["digestion"]'),
    ]
    animals = {
        1: {
            "species": "Chó",
            "breed": "Corgi",
            "gender": "Đực",
            "birth_date": (date.today() - timedelta(days=400)).isoformat(),
            "weight": 8,
            "allergies": "",
            "health_status": "Bình thường",
            "exercise_needs": "digestion",
            "behavior": "",
        }
    }
    interactions = {
        1: [
            {
                "item_id": 1,
                "event_type": "PURCHASE",
                "occurred_at": "2026-01-01 10:00:00",
                "recommendation_category": "FOOD",
                "species_tags": '["cho"]',
                "needs_tags": "[]",
            },
            {
                "item_id": 2,
                "event_type": "PURCHASE",
                "occurred_at": "2026-01-20 10:00:00",
                "recommendation_category": "FOOD",
                "species_tags": '["cho"]',
                "needs_tags": "[]",
            },
        ]
    }

    result = evaluate_recommendations(products, animals, interactions, k=1)

    assert result["sample_count"] == 1
    assert result["skipped_animals"] == 0
    assert result["hybrid"]["recall"] == 1
    assert result["hybrid"]["ndcg"] == 1
    assert result["hybrid"]["mrr"] == 1
    assert result["hybrid"]["precision"] == 1
    assert result["eligible_item_count"] == 2
    assert result["event_counts"] == {"PURCHASE": 2}
    assert result["mean_latency_ms"] >= 0


def test_evaluation_reports_insufficient_history_without_fake_scores():
    result = evaluate_recommendations(
        [evaluation_product(1)],
        {1: {"species": "Chó"}},
        {
            1: [
                {
                    "item_id": 1,
                    "event_type": "PURCHASE",
                    "occurred_at": "2026-01-01 10:00:00",
                }
            ]
        },
    )

    assert result["sample_count"] == 0
    assert result["skipped_animals"] == 1
    assert result["hybrid"] == {
        "precision": 0,
        "recall": 0,
        "ndcg": 0,
        "mrr": 0,
    }


def test_evaluation_validates_k_and_event_timestamps():
    with pytest.raises(ValueError, match="K"):
        evaluate_recommendations([], {}, {}, k=0)
    with pytest.raises(ValueError, match="Thời điểm"):
        evaluate_recommendations(
            [],
            {1: {"species": "Chó"}},
            {
                1: [
                    {"item_id": 1, "event_type": "LIKE", "occurred_at": "bad"},
                    {"item_id": 2, "event_type": "LIKE", "occurred_at": "bad"},
                ]
            },
        )
