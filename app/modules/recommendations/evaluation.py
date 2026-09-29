from __future__ import annotations

from collections import Counter
from datetime import datetime
from math import log2
from time import perf_counter
from typing import Any

from app.modules.recommendations.engine import recommend_products


POSITIVE_EVENTS = frozenset({"CLICK", "LIKE", "ADD_TO_CART", "PURCHASE", "REVIEW"})


def _timestamp(event: dict[str, Any]) -> datetime:
    try:
        return datetime.fromisoformat(str(event["occurred_at"]))
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Thời điểm tương tác không hợp lệ trong dữ liệu đánh giá.") from error


def _ranking_metrics(
    ranked_ids: list[int], relevant_ids: set[int], k: int
) -> dict[str, float]:
    top = ranked_ids[:k]
    hits = [1 if item_id in relevant_ids else 0 for item_id in top]
    relevant_hits = sum(hits)
    ideal_length = min(len(relevant_ids), k)
    dcg = sum(hit / log2(index + 2) for index, hit in enumerate(hits))
    idcg = sum(1 / log2(index + 2) for index in range(ideal_length))
    reciprocal_rank = next(
        (1 / (index + 1) for index, hit in enumerate(hits) if hit),
        0.0,
    )
    return {
        "precision": relevant_hits / k,
        "recall": relevant_hits / len(relevant_ids),
        "ndcg": dcg / idcg if idcg else 0.0,
        "mrr": reciprocal_rank,
    }


def _mean_metric(
    results: list[dict[str, float]], key: str
) -> float:
    if not results:
        return 0.0
    return sum(result[key] for result in results) / len(results)


def evaluate_recommendations(
    products: list[dict[str, Any]],
    animals: dict[int, dict[str, Any]],
    interactions_by_animal: dict[int, list[dict[str, Any]]],
    k: int = 5,
) -> dict[str, Any]:
    if k < 1:
        raise ValueError("K phải lớn hơn hoặc bằng 1.")

    hybrid_metrics: list[dict[str, float]] = []
    baseline_metrics: list[dict[str, float]] = []
    hybrid_coverage: set[int] = set()
    baseline_coverage: set[int] = set()
    latencies: list[float] = []
    eligible_items: set[int] = set()
    novelty_values: list[float] = []
    diversity_values: list[float] = []
    skipped_animals = 0
    for animal_id, animal in animals.items():
        events = interactions_by_animal.get(animal_id, [])
        timeline = sorted(
            (
                event
                for event in events
                if event.get("event_type") in POSITIVE_EVENTS
            ),
            key=_timestamp,
        )
        if len(timeline) < 2:
            skipped_animals += 1
            continue

        split_index = max(1, int(len(timeline) * 0.8))
        if split_index >= len(timeline):
            split_index = len(timeline) - 1
        training_end = _timestamp(timeline[split_index])
        relevant_ids = {
            int(event["item_id"])
            for event in timeline[split_index:]
            if int(event["item_id"]) in {int(product["item_id"]) for product in products}
        }
        if not relevant_ids:
            skipped_animals += 1
            continue
        training_events = [
            event
            for event in events
            if _timestamp(event) < training_end
        ]
        historical_counts: Counter[int] = Counter()
        for other_events in interactions_by_animal.values():
            historical_counts.update(
                int(event["item_id"])
                for event in other_events
                if event.get("event_type") in POSITIVE_EVENTS
                and _timestamp(event) < training_end
            )
        historical_total = sum(historical_counts.values())
        start = perf_counter()
        hybrid_ranked = recommend_products(products, animal, interactions=training_events)
        latencies.append((perf_counter() - start) * 1000)
        if not hybrid_ranked:
            skipped_animals += 1
            continue

        eligible_ids = {int(item["item_id"]) for item in hybrid_ranked}
        eligible_items.update(eligible_ids)
        relevant_ids &= eligible_ids
        if not relevant_ids:
            skipped_animals += 1
            continue

        hybrid_ids = [int(item["item_id"]) for item in hybrid_ranked]
        training_popularity = Counter(
            int(event["item_id"])
            for event in training_events
            if event.get("event_type") in POSITIVE_EVENTS
        )
        baseline_ranked = sorted(
            hybrid_ranked,
            key=lambda item: (
                -training_popularity[int(item["item_id"])],
                -float(item.get("popularity", 0)),
                float(item.get("recommendation_price", 0)),
                str(item.get("name", "")).casefold(),
            ),
        )
        baseline_ids = [int(item["item_id"]) for item in baseline_ranked]
        hybrid_metrics.append(_ranking_metrics(hybrid_ids, relevant_ids, k))
        baseline_metrics.append(_ranking_metrics(baseline_ids, relevant_ids, k))
        hybrid_coverage.update(hybrid_ids[:k])
        baseline_coverage.update(baseline_ids[:k])

        top_ids = hybrid_ids[:k]
        if historical_total:
            novelty_values.extend(
                -log2(
                    max(
                        historical_counts[item_id] / historical_total,
                        1 / historical_total,
                    )
                )
                for item_id in top_ids
            )
        else:
            novelty_values.extend(0.0 for _ in top_ids)

        top_items = hybrid_ranked[:k]
        pairwise_diversity = []
        for index, first in enumerate(top_items):
            first_tags = {
                str(first.get("recommendation_category", "")),
                *(
                    str(first.get(field, ""))
                    for field in (
                        "species_tags",
                        "age_groups",
                        "needs_tags",
                        "activity_tags",
                        "environment_tags",
                    )
                ),
            }
            for second in top_items[index + 1 :]:
                second_tags = {
                    str(second.get("recommendation_category", "")),
                    *(
                        str(second.get(field, ""))
                        for field in (
                            "species_tags",
                            "age_groups",
                            "needs_tags",
                            "activity_tags",
                            "environment_tags",
                        )
                    ),
                }
                union = first_tags | second_tags
                pairwise_diversity.append(
                    1 - len(first_tags & second_tags) / len(union) if union else 0.0
                )
        if pairwise_diversity:
            diversity_values.append(
                sum(pairwise_diversity) / len(pairwise_diversity)
            )
        elif top_items:
            diversity_values.append(0.0)

    sample_count = len(hybrid_metrics)
    return {
        "k": k,
        "sample_count": sample_count,
        "skipped_animals": skipped_animals,
        "eligible_item_count": len(eligible_items),
        "catalog_coverage": (
            len(hybrid_coverage) / len(eligible_items) if eligible_items else 0.0
        ),
        "baseline_catalog_coverage": (
            len(baseline_coverage) / len(eligible_items) if eligible_items else 0.0
        ),
        "hybrid": {
            metric: _mean_metric(hybrid_metrics, metric)
            for metric in ("precision", "recall", "ndcg", "mrr")
        },
        "baseline": {
            metric: _mean_metric(baseline_metrics, metric)
            for metric in ("precision", "recall", "ndcg", "mrr")
        },
        "novelty": (
            sum(novelty_values) / len(novelty_values) if novelty_values else 0.0
        ),
        "diversity": (
            sum(diversity_values) / len(diversity_values)
            if diversity_values
            else 0.0
        ),
        "mean_latency_ms": (
            sum(latencies) / len(latencies) if latencies else 0.0
        ),
        "event_counts": dict(
            Counter(
                str(event.get("event_type", "UNKNOWN"))
                for events in interactions_by_animal.values()
                for event in events
            )
        ),
    }
