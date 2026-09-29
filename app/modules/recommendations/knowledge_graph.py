from __future__ import annotations

import json
import re
import unicodedata
from typing import Any


RELATION_LABELS = {
    "SPECIES": "đúng loài",
    "AGE": "đúng giai đoạn tuổi",
    "BREED": "phù hợp giống",
    "GENDER": "phù hợp giới tính",
    "NEED": "đáp ứng nhu cầu",
    "HEALTH": "khớp thẻ sức khỏe đã cấu hình",
    "ACTIVITY": "phù hợp mức vận động",
    "COAT": "phù hợp đặc điểm lông",
    "ENVIRONMENT": "phù hợp môi trường",
}

PRODUCT_TAG_FIELDS = {
    "SPECIES": "species_tags",
    "AGE": "age_groups",
    "BREED": "breed_tags",
    "GENDER": "gender_tags",
    "NEED": "needs_tags",
    "HEALTH": "health_tags",
    "ACTIVITY": "activity_tags",
    "COAT": "coat_tags",
    "ENVIRONMENT": "environment_tags",
}


def _normalize(value: str) -> str:
    text = value.strip().casefold().replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"[\s-]+", "_", without_marks).strip("_")


def _decode_tags(value: Any) -> set[str]:
    if value is None or value == "":
        return set()
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("Thẻ sản phẩm trong đồ thị tri thức không hợp lệ.") from error
    else:
        decoded = value
    if not isinstance(decoded, (list, tuple, set)) or any(
        not isinstance(tag, str) for tag in decoded
    ):
        raise ValueError("Danh sách thẻ sản phẩm trong đồ thị tri thức không hợp lệ.")
    return {_normalize(tag) for tag in decoded if _normalize(tag)}


def _species_key(value: str) -> str:
    species = _normalize(value)
    return {
        "dog": "cho",
        "dogs": "cho",
        "cho_con": "cho",
        "cat": "meo",
        "cats": "meo",
        "meo_con": "meo",
        "rabbit": "tho",
        "guinea_pig": "guinea_pig",
        "bird": "chim",
    }.get(species, species)


def build_recommendation_paths(
    pet: dict[str, Any],
    product: dict[str, Any],
    pet_age: str | None,
    needs: set[str],
) -> list[dict[str, str]]:
    """Return explicit pet-to-product paths supported by configured catalog tags."""
    pet_values = {
        "SPECIES": {_species_key(str(pet.get("species", "")))},
        "AGE": {_normalize(pet_age)} if pet_age else set(),
        "BREED": {_normalize(str(pet.get("breed", "")))},
        "GENDER": {_normalize(str(pet.get("gender", "")))},
        "NEED": {_normalize(value) for value in needs},
        "HEALTH": {
            _normalize(str(pet.get("health_status", "")))
        } - {"", "normal", "binh_thuong"},
        "ACTIVITY": _decode_tags(pet.get("activity_tags")),
        "COAT": _decode_tags(pet.get("coat_tags")),
        "ENVIRONMENT": _decode_tags(pet.get("environment_tags")),
    }
    pet_values["GENDER"] -= {""}
    pet_values["SPECIES"] -= {""}
    product_values = {
        relation: _decode_tags(product.get(field))
        for relation, field in PRODUCT_TAG_FIELDS.items()
    }
    product_values["SPECIES"] = {
        _species_key(value) for value in product_values["SPECIES"]
    }
    product_values["GENDER"] = {
        {"male": "duc", "female": "cai"}.get(value, value)
        for value in product_values["GENDER"]
    }
    pet_values["GENDER"] = {
        {"male": "duc", "female": "cai"}.get(value, value)
        for value in pet_values["GENDER"]
    }

    paths = []
    for relation, pet_tags in pet_values.items():
        configured_tags = product_values.get(relation, set())
        if not configured_tags:
            continue
        for matched in sorted(pet_tags & configured_tags):
            paths.append(
                {
                    "relation": relation,
                    "pet_value": matched,
                    "product_value": matched,
                    "label": RELATION_LABELS[relation],
                }
            )
    return paths
