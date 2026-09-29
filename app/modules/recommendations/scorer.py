from __future__ import annotations

from typing import Any

from app.modules.recommendations.engine import (
    _history_score,
    _need_score,
    _pet_needs,
    age_group,
    species_key,
)


def score_candidates(
    products: list[dict[str, Any]],
    pet: dict[str, Any],
    interactions: list[dict[str, Any]] | None = None,
    selected_needs: set[str] | None = None,
    collaborative_interactions: list[dict[str, Any]] | None = None,
    product_preferences: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Attach a weighted score and score breakdown to candidates."""
    history = interactions or []
    peer_history = collaborative_interactions or []
    selected_needs = selected_needs or set()
    pet_needs = _pet_needs(pet, selected_needs)
    pet_species = species_key(str(pet.get("species", "")))
    pet_breed = str(pet.get("breed", "")).strip()
    pet_gender = str(pet.get("gender", "")).strip()
    pet_age = age_group(str(pet.get("birth_date", "")))
    preferences = {
        int(pref["item_id"]): str(pref["preference"])
        for pref in (product_preferences or [])
    }

    scored: list[dict[str, Any]] = []
    for product in products:
        category = str(product.get("recommendation_category", "OTHER"))
        product_species = {species_key(tag) for tag in str(product.get("species_tags", "")).split(",") if tag.strip()}
        if product_species and pet_species not in product_species:
            continue

        item_preference = preferences.get(int(product.get("item_id", -1)))
        history_score = _history_score(product, history, purchase_only=False)
        purchase_score = _history_score(product, history, purchase_only=True)
        needs_score = _need_score(product, pet_needs)

        score = (
            30 * (100 if not product_species or pet_species in product_species else 10) / 100
            + 15 * (100 if pet_age and str(product.get("age_groups", "")).lower().find(str(pet_age).lower()) >= 0 else 20) / 100
            + 15 * (100 if not pet_breed or str(product.get("breed_tags", "")).lower().find(str(pet_breed).lower()) >= 0 else 25) / 100
            + 15 * (needs_score / 100)
            + 10 * (history_score / 100)
            + 5 * (float(product.get("popularity", 0)) / 100)
            + 5 * (100 if item_preference == "LIKE" else 50) / 100
            + 5 * (100 if product.get("usable_quantity", 0) else 25) / 100
        )

        score = round(min(100, max(0, score)), 2)
        product_with_score = dict(product)
        product_with_score["score"] = score
        product_with_score["score_breakdown"] = {
            "species": 100 if not product_species or pet_species in product_species else 10,
            "age": 100 if pet_age and str(product.get("age_groups", "")).lower().find(str(pet_age).lower()) >= 0 else 20,
            "breed": 100 if not pet_breed or str(product.get("breed_tags", "")).lower().find(str(pet_breed).lower()) >= 0 else 25,
            "needs": needs_score,
            "history": history_score,
            "purchase_history": purchase_score,
            "popularity": min(100, float(product.get("popularity", 0))),
            "stock": 100 if product.get("usable_quantity", 0) else 25,
        }
        product_with_score["reasons"] = [
            "Phù hợp loài",
            "Còn hàng",
            "Khớp nhu cầu",
        ]
        if pet_age and str(product.get("age_groups", "")).lower().find(str(pet_age).lower()) >= 0:
            product_with_score["reasons"].append("Phù hợp độ tuổi")
        if item_preference == "LIKE":
            product_with_score["reasons"].append("Khách hàng đã lưu mục ưa thích")
        scored.append(product_with_score)

    return scored
