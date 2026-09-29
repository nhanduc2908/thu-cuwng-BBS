from __future__ import annotations

from datetime import date, datetime
import json
import math
import re
from typing import Any

from app.modules.recommendations.constants import RECOMMENDATION_SCORE_WEIGHTS
from app.modules.recommendations.knowledge_graph import build_recommendation_paths


def normalize_tag(value: str) -> str:
    normalized = re.sub(r"[\s-]+", "_", value.strip().casefold())
    return normalized.strip("_")


def parse_tags(value: str | list[str] | tuple[str, ...] | None) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        values = re.split(r"[,;，；\n]+", value)
    else:
        values = value
    return {tag for raw in values if (tag := normalize_tag(str(raw)))}


def _json_tags(value: str | list[str] | None) -> set[str]:
    if isinstance(value, list):
        return parse_tags(value)
    if not value:
        return set()
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("Dữ liệu thẻ sản phẩm trong cơ sở dữ liệu bị lỗi.") from error
    if not isinstance(decoded, list) or any(not isinstance(tag, str) for tag in decoded):
        raise ValueError("Danh sách thẻ sản phẩm không hợp lệ.")
    return parse_tags(decoded)


def species_key(species: str) -> str:
    value = normalize_tag(species)
    aliases = {
        "dog": "cho",
        "dogs": "cho",
        "chó": "cho",
        "cat": "meo",
        "cats": "meo",
        "mèo": "meo",
        "rabbit": "tho",
        "thỏ": "tho",
        "hamster": "hamster",
        "bird": "chim",
        "chim": "chim",
        "guinea_pig": "guinea_pig",
        "turtle": "rua",
        "tortoise": "rua",
        "rùa": "rua",
        "fish": "ca",
        "cá": "ca",
        "exotic": "exotic",
        "exotic_pet": "exotic",
    }
    return aliases.get(value, value)


def age_group(birth_date: str, today: date | None = None) -> str | None:
    if not birth_date:
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    current = today or date.today()
    if born > current:
        return None
    months = (current.year - born.year) * 12 + current.month - born.month
    if current.day < born.day:
        months -= 1
    if months < 3:
        return "baby"
    if months < 12:
        return "young"
    years = months / 12
    return "senior" if years >= 8 else "adult"


def age_in_months(birth_date: str, today: date | None = None) -> int | None:
    if not birth_date:
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    current = today or date.today()
    if born > current:
        return None
    months = (current.year - born.year) * 12 + current.month - born.month
    if current.day < born.day:
        months -= 1
    return months


def _age_score(product: dict[str, Any], pet_age: str | None) -> float:
    tags = _json_tags(product.get("age_groups"))
    if not tags:
        return 100
    if pet_age is None:
        return 50
    return 100 if pet_age in tags else 10


def _breed_score(product: dict[str, Any], breed: str) -> float:
    tags = _json_tags(product.get("breed_tags"))
    if not tags:
        return 100
    if not breed:
        return 40
    breed_tag = normalize_tag(breed)
    return 100 if breed_tag in tags else 15


def _gender_score(product: dict[str, Any], gender: str) -> float:
    tags = _json_tags(product.get("gender_tags"))
    if not tags:
        return 100
    value = normalize_tag(gender)
    if not value:
        return 50
    value = {"male": "đực", "female": "cái"}.get(value, value)
    return 100 if value in tags else 10


def _need_score(product: dict[str, Any], needs: set[str]) -> float:
    product_needs = (
        _json_tags(product.get("needs_tags"))
        | _json_tags(product.get("health_tags"))
        | _json_tags(product.get("activity_tags"))
        | _json_tags(product.get("coat_tags"))
        | _json_tags(product.get("environment_tags"))
    )
    if not needs:
        return 50
    if not product_needs:
        return 40
    matched = len(needs & product_needs)
    return min(100, 35 + (65 * matched / len(needs)))


def _interaction_similarity(
    candidate: dict[str, Any], interacted: dict[str, Any]
) -> float:
    def purpose_tags(product: dict[str, Any]) -> set[str]:
        direct = product.get("purpose_tags")
        if direct:
            return _json_tags(direct)
        category = product.get("recommendation_category")
        return parse_tags(str(category)) if category else set()

    candidate_tags = (
        _json_tags(candidate.get("needs_tags"))
        | _json_tags(candidate.get("health_tags"))
        | purpose_tags(candidate)
        | _json_tags(candidate.get("activity_tags"))
        | _json_tags(candidate.get("coat_tags"))
        | _json_tags(candidate.get("environment_tags"))
    )
    previous_tags = (
        _json_tags(interacted.get("needs_tags"))
        | _json_tags(interacted.get("health_tags"))
        | purpose_tags(interacted)
        | _json_tags(interacted.get("activity_tags"))
        | _json_tags(interacted.get("coat_tags"))
        | _json_tags(interacted.get("environment_tags"))
    )
    if candidate.get("item_id") == interacted.get("item_id"):
        return 1.0
    if not candidate_tags or not previous_tags:
        return 0.0
    return len(candidate_tags & previous_tags) / len(candidate_tags | previous_tags)


def _history_score(
    product: dict[str, Any],
    interactions: list[dict[str, Any]],
    purchase_only: bool,
) -> float:
    event_weights = {
        "VIEW": 1,
        "CLICK": 2,
        "SEARCH": 1,
        "LIKE": 4,
        "ADD_TO_CART": 5,
        "PURCHASE": 7,
        "REVIEW": 6,
        "REMOVE_CART": -4,
    }
    weighted = 0.0
    total_weight = 0.0
    for interaction in interactions:
        event = interaction.get("event_type", "")
        if purchase_only and event != "PURCHASE":
            continue
        if event not in event_weights:
            continue
        magnitude = abs(event_weights[event])
        recency = 1.0
        occurred_at = interaction.get("occurred_at")
        if occurred_at:
            try:
                happened = datetime.fromisoformat(str(occurred_at))
            except ValueError as error:
                raise ValueError("Thời điểm hành vi sản phẩm không hợp lệ.") from error
            age_days = max(
                0.0,
                (datetime.now() - happened).total_seconds() / 86400,
            )
            recency = 0.5 ** (age_days / 60)
        similarity = _interaction_similarity(product, interaction)
        if similarity == 0:
            continue
        weight = event_weights[event]
        weighted += weight * similarity * recency
        total_weight += magnitude * recency
    if total_weight == 0:
        return 50
    return max(0, min(100, 50 + 50 * weighted / total_weight))


def _collaborative_score(
    product: dict[str, Any],
    interactions: list[dict[str, Any]],
    peer_interactions: list[dict[str, Any]],
) -> float:
    anchors = {
        int(interaction["item_id"])
        for interaction in interactions
        if interaction.get("event_type")
        in {"VIEW", "CLICK", "LIKE", "ADD_TO_CART", "PURCHASE"}
    }
    if not anchors:
        return 50
    peers = {
        int(interaction["peer_animal_id"])
        for interaction in peer_interactions
        if int(interaction["item_id"]) == int(product.get("item_id", -1))
        and int(interaction["anchor_item_id"]) in anchors
        and interaction.get("event_type")
        in {"LIKE", "ADD_TO_CART", "PURCHASE", "REVIEW"}
    }
    if not peers:
        return 50
    return min(100, 50 + 20 * math.log2(1 + len(peers)))


def _pet_needs(pet: dict[str, Any], selected_needs: set[str]) -> set[str]:
    needs = set(selected_needs)
    for field in ("allergies", "exercise_needs", "behavior"):
        needs.update(parse_tags(str(pet.get(field, ""))))
    health_status = normalize_tag(str(pet.get("health_status", "")))
    if health_status not in {"", "bình_thường", "normal"}:
        needs.add(health_status)
    return needs


def recommend_products(
    products: list[dict[str, Any]],
    pet: dict[str, Any],
    interactions: list[dict[str, Any]] | None = None,
    selected_needs: set[str] | None = None,
    purpose: str | None = None,
    minimum_price: float | None = None,
    maximum_price: float | None = None,
    collaborative_interactions: list[dict[str, Any]] | None = None,
    product_preferences: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Rank safe, in-stock products with an explainable weighted rule score."""
    pet_species = species_key(str(pet.get("species", "")))
    pet_breed = str(pet.get("breed", "")).strip()
    pet_gender = str(pet.get("gender", "")).strip()
    pet_age = age_group(str(pet.get("birth_date", "")))
    pet_age_months = age_in_months(str(pet.get("birth_date", "")))
    needs = _pet_needs(pet, selected_needs or set())
    allergy_tags = parse_tags(str(pet.get("allergies", "")))
    history = interactions or []
    peer_history = collaborative_interactions or []
    preferences = {
        int(preference["item_id"]): str(preference["preference"])
        for preference in (product_preferences or [])
    }
    if any(value not in {"LIKE", "AVOID"} for value in preferences.values()):
        raise ValueError("Dữ liệu ghi nhớ sở thích sản phẩm không hợp lệ.")
    results: list[dict[str, Any]] = []

    for product in products:
        category = str(product.get("recommendation_category", "OTHER"))
        if category == "VETERINARY":
            continue
        product_species = {
            species_key(tag) for tag in _json_tags(product.get("species_tags"))
        }
        if product_species and pet_species not in product_species:
            continue
        age_unit = str(product.get("age_unit", "MONTH")).upper()
        minimum_age = product.get("age_min_months")
        maximum_age = product.get("age_max_months")
        if pet_age_months is not None and age_unit != "LABEL":
            age_multiplier = 12 if age_unit == "YEAR" else 1
            minimum_age = float(minimum_age) if minimum_age is not None else None
            maximum_age = float(maximum_age) if maximum_age is not None else None
            if minimum_age is not None and pet_age_months < minimum_age * age_multiplier:
                continue
            if maximum_age is not None and pet_age_months > maximum_age * age_multiplier:
                continue
        avoid_tags = _json_tags(product.get("avoid_tags"))
        if allergy_tags & avoid_tags:
            continue
        item_preference = preferences.get(int(product.get("item_id", -1)))
        if item_preference == "AVOID":
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
        minimum_weight = product.get("minimum_weight")
        maximum_weight = product.get("maximum_weight")
        weight = pet.get("weight")
        minimum_weight = float(minimum_weight) if minimum_weight is not None else None
        maximum_weight = float(maximum_weight) if maximum_weight is not None else None
        weight = float(weight) if weight is not None else None
        if weight is not None and minimum_weight is not None and weight < minimum_weight:
            continue
        if weight is not None and maximum_weight is not None and weight > maximum_weight:
            continue
        suitable_minimum = product.get("suitable_weight_min")
        suitable_maximum = product.get("suitable_weight_max")
        if weight is not None and suitable_minimum is not None:
            if weight < float(suitable_minimum):
                continue
        if weight is not None and suitable_maximum is not None:
            if weight > float(suitable_maximum):
                continue

        needs_score = _need_score(product, needs)
        if purpose and purpose != "ALL":
            needs_score = max(needs_score, 85)
        behavior_score = (
            0.6 * _history_score(product, history, purchase_only=False)
            + 0.4 * _collaborative_score(product, history, peer_history)
        )
        if item_preference == "LIKE":
            behavior_score = max(behavior_score, 100)
        breakdown = {
            "species": 100,
            "age": _age_score(product, pet_age),
            "breed": (
                _breed_score(product, pet_breed) * 0.8
                + _gender_score(product, pet_gender) * 0.2
            ),
            "needs": needs_score,
            "behavior": behavior_score,
            "purchase_history": _history_score(product, history, purchase_only=True),
            "popularity": max(0, min(100, float(product.get("popularity", 0)))),
            "stock": 100,
        }
        score = round(
            sum(
                breakdown[key] * weight_value / 100
                for key, weight_value in RECOMMENDATION_SCORE_WEIGHTS.items()
            ),
            2,
        )
        reasons = ["Đúng loài", "Còn hàng"]
        if pet_age and _age_score(product, pet_age) == 100:
            reasons.append("Phù hợp độ tuổi")
        if pet_breed and _breed_score(product, pet_breed) == 100:
            reasons.append("Phù hợp giống")
        if needs and needs_score > 50:
            reasons.append("Có thẻ phù hợp nhu cầu")
        if breakdown["behavior"] > 50:
            reasons.append("Khớp hành vi quan tâm")
        if breakdown["purchase_history"] > 50:
            reasons.append("Liên quan lịch sử mua")
        if item_preference == "LIKE":
            reasons.append("Đã lưu trong sở thích của bé")
        knowledge_paths = build_recommendation_paths(
            pet,
            product,
            pet_age,
            needs,
        )
        results.append(
            {
                **product,
                "score": score,
                "score_breakdown": breakdown,
                "reasons": reasons,
                "knowledge_paths": knowledge_paths,
            }
        )

    return sorted(
        results,
        key=lambda result: (
            -result["score"],
            float(result.get("recommendation_price", 0)),
            str(result.get("name", "")).casefold(),
        ),
    )


def encode_tags(value: str | list[str] | tuple[str, ...] | None) -> str:
    return json.dumps(sorted(parse_tags(value)), ensure_ascii=False)
