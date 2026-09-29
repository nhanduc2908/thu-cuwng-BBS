from __future__ import annotations

from typing import Any


def build_recommendation_explanation(
    pet: dict[str, Any],
    item: dict[str, Any],
    package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Turn a scored recommendation into a human-safe explanation with evidence."""
    pet_name = str(pet.get("name") or pet.get("pet_name") or "bé thú cưng")
    item_name = str(item.get("name") or item.get("item_name") or "sản phẩm")
    score = float(item.get("score", 0.0))
    reasons = item.get("reasons") or []
    score_breakdown = item.get("score_breakdown") or {}
    top_factors = [
        key
        for key, value in sorted(
            score_breakdown.items(),
            key=lambda pair: float(pair[1]),
            reverse=True,
        )[:3]
    ]

    explanation = (
        f"{pet_name} phù hợp với {item_name} vì hệ thống đánh giá mức độ phù hợp là {score:.1f}/100. "
        f"Điểm mạnh nhất đến từ {', '.join(top_factors) if top_factors else 'độ khớp tổng thể'}."
    )
    if reasons:
        explanation += " Các dấu hiệu khớp gồm: " + "; ".join(reasons[:4]) + "."

    evidence = {
        "pet_species": pet.get("species", ""),
        "pet_breed": pet.get("breed", "") or pet.get("breed_name", ""),
        "pet_age": pet.get("birth_date", ""),
        "item_category": item.get("recommendation_category", "OTHER"),
        "score": round(score, 2),
        "top_factors": top_factors,
        "reasons": reasons,
        "guardrail": "Thông tin này chỉ là gợi ý hỗ trợ, không thay thế chẩn đoán thú y.",
    }
    if package:
        evidence["package_summary"] = package.get("filters", {})

    return {
        "summary": explanation,
        "evidence": evidence,
        "tone": "SAFE_AND_EXPLAINABLE",
    }


def explain_recommendations(
    pet: dict[str, Any],
    result_items: list[dict[str, Any]],
    package: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Create a structured explanation for each item in a recommendation package."""
    return [
        build_recommendation_explanation(pet, item, package=package)
        for item in result_items
    ]
