from __future__ import annotations

from typing import Any


def evaluate_governance(
    model_name: str,
    metrics: dict[str, Any],
    evidence: dict[str, Any] | None = None,
    policies: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check whether a model can be promoted under the project safety policy."""
    evidence = evidence or {}
    policies = policies or {
        "min_samples": 20,
        "min_average_rating": 3.8,
        "min_conversion_rate": 0.2,
        "must_have_evidence": True,
    }

    sample_count = int(metrics.get("samples", 0))
    avg_rating = float(metrics.get("avg_rating", 0.0))
    conversion_rate = float(metrics.get("conversion_rate", 0.0))
    evidence_ok = bool(evidence.get("guardrail", False)) or bool(evidence.get("supporting_docs"))

    result = {
        "model_name": model_name,
        "approved": False,
        "checks": {
            "samples": sample_count >= int(policies.get("min_samples", 20)),
            "rating": avg_rating >= float(policies.get("min_average_rating", 3.8)),
            "conversion": conversion_rate >= float(policies.get("min_conversion_rate", 0.2)),
            "evidence": evidence_ok,
        },
    }
    result["approved"] = all(result["checks"].values())
    return result


def policy_summary(model_name: str, state: dict[str, Any]) -> str:
    checks = state.get("checks", {})
    passed = sum(1 for value in checks.values() if value)
    total = len(checks)
    return f"{model_name}: {passed}/{total} policy checks passed."
