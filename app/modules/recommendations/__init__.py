"""Recommendation engine modules for product ranking, explanation and lifecycle management."""

from app.modules.recommendations.explanation import (
    build_recommendation_explanation,
    explain_recommendations,
)
from app.modules.recommendations.feedback_loop import aggregate_feedback, record_feedback
from app.modules.recommendations.filters import filter_candidates
from app.modules.recommendations.governance import evaluate_governance, policy_summary
from app.modules.recommendations.ml_pipeline import (
    build_training_dataset,
    evaluate_dataset,
    prepare_training_snapshot,
)
from app.modules.recommendations.model_registry import (
    latest_model,
    list_registered_models,
    register_model,
)
from app.modules.recommendations.package_builder import build_recommendation_package
from app.modules.recommendations.ranker import rank_candidates
from app.modules.recommendations.scorer import score_candidates

__all__ = [
    "filter_candidates",
    "score_candidates",
    "rank_candidates",
    "build_recommendation_package",
    "build_recommendation_explanation",
    "explain_recommendations",
    "record_feedback",
    "aggregate_feedback",
    "build_training_dataset",
    "evaluate_dataset",
    "prepare_training_snapshot",
    "register_model",
    "list_registered_models",
    "latest_model",
    "evaluate_governance",
    "policy_summary",
]
