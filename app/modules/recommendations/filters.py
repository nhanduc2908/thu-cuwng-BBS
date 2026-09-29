from __future__ import annotations

from typing import Any

from app.modules.recommendations.engine import (
    _json_tags,
    age_in_months,
    parse_tags,
    species_key,
)


def filter_candidates(
    products: list[dict[str, Any]],
    pet: dict[str, Any],
    selected_needs: set[str] | None = None,
    purpose: str | None = None,
    minimum_price: float | None = None,
    maximum_price: float | None = None,
) -> list[dict[str, Any]]:
    """Keep only products that match pet species, age, stock, price and safety rules."""
    pet_species = species_key(str(pet.get("species", "")))
    pet_age_months = age_in_months(str(pet.get("birth_date", "")))
    selected_needs = selected_needs or set()
    allergy_tags = parse_tags(str(pet.get("allergies", "")))

    candidates: list[dict[str, Any]] = []
    for product in products:
        category = str(product.get("recommendation_category", "OTHER"))
        if category == "VETERINARY":
            continue

        product_species = {species_key(tag) for tag in _json_tags(product.get("species_tags"))}
        if product_species and pet_species not in product_species:
            continue

        age_unit = str(product.get("age_unit", "MONTH")).upper()
        minimum_age = product.get("age_min_months")
        maximum_age = product.get("age_max_months")
        if pet_age_months is not None and age_unit != "LABEL":
            multiplier = 12 if age_unit == "YEAR" else 1
            min_value = float(minimum_age) if minimum_age is not None else None
            max_value = float(maximum_age) if maximum_age is not None else None
            if min_value is not None and pet_age_months < min_value * multiplier:
                continue
            if max_value is not None and pet_age_months > max_value * multiplier:
                continue

        avoid_tags = _json_tags(product.get("avoid_tags"))
        if allergy_tags & avoid_tags:
            continue

        stock = float(product.get("usable_quantity", 0))
        if stock <= 0:
            continue

        price = float(product.get("recommendation_price", 0))
        if minimum_price is not None and price < minimum_price:
            continue
        if maximum_price is not None and price > maximum_price:
            continue

        if purpose and purpose != "ALL" and category != purpose:
            continue

        weight = pet.get("weight")
        weight_value = float(weight) if weight is not None else None
        min_weight = product.get("minimum_weight")
        max_weight = product.get("maximum_weight")
        min_weight_value = float(min_weight) if min_weight is not None else None
        max_weight_value = float(max_weight) if max_weight is not None else None
        if weight_value is not None and min_weight_value is not None and weight_value < min_weight_value:
            continue
        if weight_value is not None and max_weight_value is not None and weight_value > max_weight_value:
            continue

        if selected_needs and _json_tags(product.get("avoid_tags")) & selected_needs:
            continue

        candidates.append(product)

    return candidates
