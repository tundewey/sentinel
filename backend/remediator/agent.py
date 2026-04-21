"""Remediator agent for next-action recommendations."""

from __future__ import annotations

from common.bedrock import converse_json
from common.config import model_remediation
from common.guardrails import enforce_grounding
from common.heuristics import recommend_actions
from common.models import IncidentSummary, NormalizedIncident, RemediationPlan, RootCauseAnalysis
from remediator.templates import REMEDIATOR_INSTRUCTIONS


def generate_remediation(
    normalized: NormalizedIncident,
    summary: IncidentSummary,
    root_cause: RootCauseAnalysis,
) -> RemediationPlan:
    """Generate remediation recommendations with guardrail enforcement."""

    prompt = (
        "Return strict JSON with keys: recommended_actions, next_checks, risk_if_unresolved.\n"
        f"Severity: {summary.severity}\n"
        f"Root cause: {root_cause.model_dump_json()}\n"
        f"Evidence: {normalized.evidence_snippets}"
    )
    result = converse_json(model_remediation(), REMEDIATOR_INSTRUCTIONS, prompt)

    if result:
        try:
            rem = RemediationPlan.model_validate(result)
            _, rem = enforce_grounding(root_cause, rem, normalized.evidence_snippets)
            return rem
        except Exception:  # noqa: BLE001
            pass

    rem = recommend_actions(root_cause, summary.severity)
    _, rem = enforce_grounding(root_cause, rem, normalized.evidence_snippets)
    return rem
