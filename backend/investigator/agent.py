"""Investigator agent for root-cause identification."""

from __future__ import annotations

from common.bedrock import converse_json
from common.config import model_root_cause
from common.guardrails import enforce_grounding
from common.heuristics import infer_root_cause
from common.models import IncidentSummary, NormalizedIncident, RemediationPlan, RootCauseAnalysis
from investigator.templates import INVESTIGATOR_INSTRUCTIONS


def investigate_root_cause(normalized: NormalizedIncident, summary: IncidentSummary) -> RootCauseAnalysis:
    """Identify likely root cause with grounded evidence."""

    prompt = (
        "Return strict JSON with keys: likely_root_cause, confidence, reasoning, supporting_evidence.\n"
        f"Summary: {summary.summary}\n"
        f"Evidence: {normalized.evidence_snippets}\n"
        f"Log text: {normalized.normalized_text[:4000]}"
    )
    result = converse_json(model_root_cause(), INVESTIGATOR_INSTRUCTIONS, prompt)

    if result:
        try:
            rc = RootCauseAnalysis.model_validate(result)
            rc, _ = enforce_grounding(
                rc,
                RemediationPlan(recommended_actions=[], next_checks=[], risk_if_unresolved=""),
                normalized.evidence_snippets,
            )
            return rc
        except Exception:  # noqa: BLE001
            pass

    rc = infer_root_cause(normalized.normalized_text, normalized.evidence_snippets)
    rc, _ = enforce_grounding(
        rc,
        RemediationPlan(recommended_actions=[], next_checks=[], risk_if_unresolved=""),
        normalized.evidence_snippets,
    )
    return rc
