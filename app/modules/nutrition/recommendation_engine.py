from __future__ import annotations

from typing import Any, Dict, Iterable, List


SPECIES_ALIASES = {
    "dog": "DOG",
    "dogs": "DOG",
    "cho": "DOG",
    "chó": "DOG",
    "cat": "CAT",
    "cats": "CAT",
    "mèo": "CAT",
    "meo": "CAT",
}


def _normalize_species(value: Any) -> str:
    return SPECIES_ALIASES.get(str(value).strip().lower(), str(value).strip().upper())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def build_pet_nutrition_profile(pet_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Create a simplified nutrition profile from a pet record."""
    species = _normalize_species(pet_profile.get("species", "DOG"))
    age_months = int(pet_profile.get("age_months") or pet_profile.get("age") or 0)
    weight_kg = _safe_float(pet_profile.get("weight_kg") or pet_profile.get("weight") or 0.0)
    activity = str(pet_profile.get("activity_level", "MEDIUM")).upper()
    body_condition = str(pet_profile.get("body_condition", "NORMAL")).upper()
    allergies = set(str(pet_profile.get("allergies", "")).split(","))
    allergies = {item.strip() for item in allergies if item.strip()}

    protein_level = "HIGH" if weight_kg >= 20 or activity in {"HIGH", "VERY_HIGH"} else "MODERATE"
    fat_level = "MODERATE"
    fiber_level = "MODERATE"
    energy_level = "HIGH" if activity in {"HIGH", "VERY_HIGH"} else "MEDIUM"

    if age_months <= 12:
        protein_level = "HIGH"
        fat_level = "MODERATE"
    elif age_months >= 120:
        protein_level = "MODERATE"
        fat_level = "LOW"
        fiber_level = "HIGH"
        energy_level = "LOW" if activity in {"LOW", "SEDENTARY"} else "MEDIUM"

    if body_condition in {"OVERWEIGHT", "FAT"}:
        fat_level = "LOW"
        fiber_level = "HIGH"
    elif body_condition in {"UNDERWEIGHT", "LEAN"}:
        fat_level = "MODERATE"
        protein_level = "HIGH"

    return {
        "species": species,
        "age_months": age_months,
        "weight_kg": weight_kg,
        "activity_level": activity,
        "body_condition": body_condition,
        "protein_level": protein_level,
        "fat_level": fat_level,
        "fiber_level": fiber_level,
        "energy_level": energy_level,
        "allergies": allergies,
    }


def _score_food(pet_profile: Dict[str, Any], food: Dict[str, Any]) -> float:
    score = 0.0
    food_species = _normalize_species(food.get("species", ""))
    pet_species = _normalize_species(pet_profile.get("species", ""))
    if food_species and pet_species and food_species == pet_species:
        score += 35
    else:
        score -= 20

    life_stage = str(food.get("life_stage", "ADULT")).upper()
    pet_age_months = int(pet_profile.get("age_months") or 0)
    if life_stage == "PUPPY" and pet_age_months <= 12:
        score += 20
    elif life_stage == "ADULT" and pet_age_months > 12 and pet_age_months < 120:
        score += 15
    elif life_stage == "SENIOR" and pet_age_months >= 120:
        score += 18

    pet_activity = str(pet_profile.get("activity_level", "MEDIUM")).upper()
    if pet_activity in {"HIGH", "VERY_HIGH"}:
        score += 10 if str(food.get("food_type", "DRY")).upper() == "DRY" else 5
    else:
        score += 5

    pet_allergies = pet_profile.get("allergies", set())
    food_allergens = {str(item).strip() for item in food.get("allergens", []) if str(item).strip()}
    if pet_allergies and food_allergens and pet_allergies & food_allergens:
        score -= 50

    food_nutrition = food.get("nutrition", {})
    protein_percent = _safe_float(food_nutrition.get("protein_percent"), 0.0)
    fat_percent = _safe_float(food_nutrition.get("fat_percent"), 0.0)
    fiber_percent = _safe_float(food_nutrition.get("fiber_percent"), 0.0)

    protein_target = {"HIGH": 28, "MODERATE": 20, "LOW": 16}.get(pet_profile.get("protein_level", "MODERATE"), 20)
    fat_target = {"HIGH": 18, "MODERATE": 14, "LOW": 10}.get(pet_profile.get("fat_level", "MODERATE"), 14)
    fiber_target = {"HIGH": 6, "MODERATE": 4, "LOW": 2}.get(pet_profile.get("fiber_level", "MODERATE"), 4)

    score += _clamp((protein_percent / max(1.0, protein_target)) * 10)
    score += _clamp((fat_percent / max(1.0, fat_target)) * 10)
    score += _clamp((fiber_percent / max(1.0, fiber_target)) * 10)

    if pet_profile.get("body_condition") in {"OVERWEIGHT", "FAT"} and fiber_percent >= 4:
        score += 10
    if pet_profile.get("body_condition") in {"UNDERWEIGHT", "LEAN"} and protein_percent >= 24:
        score += 8

    score = _clamp(score, 0, 100)
    return round(score, 2)


def recommend_foods_for_pet(pet_profile: Dict[str, Any], foods: Iterable[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Recommend foods with a nutrition-aware score based on species, age, activity and allergies."""
    normalized_pet = build_pet_nutrition_profile(pet_profile)
    ranked = []
    for food in foods:
        recommended = dict(food)
        score = _score_food(normalized_pet, food)
        recommended["nutrition_score"] = score
        recommended["nutrition_profile"] = {
            "species": normalized_pet["species"],
            "age_months": normalized_pet["age_months"],
            "activity_level": normalized_pet["activity_level"],
            "protein_level": normalized_pet["protein_level"],
            "fat_level": normalized_pet["fat_level"],
            "fiber_level": normalized_pet["fiber_level"],
            "energy_level": normalized_pet["energy_level"],
        }
        ranked.append(recommended)

    ranked.sort(key=lambda item: (-float(item.get("nutrition_score", 0)), str(item.get("product_name", ""))))
    return ranked[:limit]
