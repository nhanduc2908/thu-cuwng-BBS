from __future__ import annotations

from typing import Any


def build_training_dataset(
    recommendation_history: list[dict[str, Any]],
    feedback_rows: list[dict[str, Any]],
    product_catalog: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create a lightweight training-ready dataset from past behavior."""
    catalog_by_id = {int(item.get("item_id", item.get("id"))): item for item in product_catalog}
    dataset: list[dict[str, Any]] = []
    for event in recommendation_history:
        item_id = int(event.get("item_id", -1))
        product = catalog_by_id.get(item_id, {})
        feedback = next(
            (
                row
                for row in feedback_rows
                if int(row.get("customer_id", -1)) == int(event.get("customer_id", -1))
                and int(row.get("pet_id", -1)) == int(event.get("pet_id", -1))
            ),
            {},
        )
        dataset.append(
            {
                "customer_id": event.get("customer_id"),
                "pet_id": event.get("pet_id"),
                "item_id": item_id,
                "item_category": product.get("recommendation_category", "OTHER"),
                "score": float(event.get("score", 0.0)),
                "rating": int(feedback.get("rating", 0)),
                "event_type": event.get("event_type", "VIEW"),
                "species": event.get("species", ""),
                "breed": event.get("breed", ""),
            }
        )
    return dataset


def evaluate_dataset(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    """Return summary statistics for model evaluation."""
    if not dataset:
        return {"samples": 0, "avg_score": 0.0, "avg_rating": 0.0, "conversion_rate": 0.0}

    scores = [float(row.get("score", 0.0)) for row in dataset]
    ratings = [int(row.get("rating", 0)) for row in dataset]
    conversions = sum(1 for row in dataset if row.get("event_type") in {"PURCHASE", "BOOKING"})
    return {
        "samples": len(dataset),
        "avg_score": round(sum(scores) / len(scores), 2),
        "avg_rating": round(sum(ratings) / len(ratings), 2),
        "conversion_rate": round(conversions / len(dataset), 2),
    }


def prepare_training_snapshot(
    recommendation_history: list[dict[str, Any]],
    feedback_rows: list[dict[str, Any]],
    product_catalog: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepare a compact dataset snapshot for the training and model registry pipeline."""
    dataset = build_training_dataset(recommendation_history, feedback_rows, product_catalog)
    return {
        "dataset": dataset,
        "metrics": evaluate_dataset(dataset),
        "sample_count": len(dataset),
    }
