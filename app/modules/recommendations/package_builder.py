from __future__ import annotations

from typing import Any

from app.modules.recommendations.filters import filter_candidates
from app.modules.recommendations.ranker import rank_candidates
from app.modules.recommendations.scorer import score_candidates


def build_recommendation_package(
    products: list[dict[str, Any]],
    pet: dict[str, Any],
    interactions: list[dict[str, Any]] | None = None,
    selected_needs: set[str] | None = None,
    purpose: str | None = None,
    minimum_price: float | None = None,
    maximum_price: float | None = None,
    collaborative_interactions: list[dict[str, Any]] | None = None,
    product_preferences: list[dict[str, Any]] | None = None,
    top_n: int = 5,
) -> dict[str, Any]:
    """Create a structured recommendation package for UI or LLM rendering."""
    filtered = filter_candidates(
        products,
        pet,
        selected_needs=selected_needs,
        purpose=purpose,
        minimum_price=minimum_price,
        maximum_price=maximum_price,
    )
    scored = score_candidates(
        filtered,
        pet,
        interactions=interactions,
        selected_needs=selected_needs,
        collaborative_interactions=collaborative_interactions,
        product_preferences=product_preferences,
    )
    ranked = rank_candidates(scored)
    package = {
        "pet": {
            "name": pet.get("name", ""),
            "species": pet.get("species", ""),
            "breed": pet.get("breed", "") or pet.get("breed_name", ""),
            "age": pet.get("birth_date", ""),
            "weight": pet.get("weight"),
        },
        "filters": {
            "purpose": purpose,
            "selected_needs": sorted(selected_needs or []),
            "minimum_price": minimum_price,
            "maximum_price": maximum_price,
        },
        "items": [
            {
                "item_id": int(item.get("item_id", 0)),
                "name": item.get("name", ""),
                "category": item.get("recommendation_category", "OTHER"),
                "score": float(item.get("score", 0)),
                "score_breakdown": item.get("score_breakdown", {}),
                "reasons": item.get("reasons", []),
                "recommendation_price": item.get("recommendation_price", 0),
            }
            for item in ranked[:top_n]
        ],
    }
    return package
