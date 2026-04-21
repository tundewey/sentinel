"""Normalizer agent implementation."""

from __future__ import annotations

from common.guardrails import extract_evidence_snippets, sanitize_incident_text
from common.models import NormalizedIncident


def normalize_incident(raw_text: str) -> NormalizedIncident:
    """Sanitize input and extract evidence snippets for downstream agents."""

    sanitized, report = sanitize_incident_text(raw_text)
    evidence = extract_evidence_snippets(sanitized)
    return NormalizedIncident(
        normalized_text=sanitized,
        evidence_snippets=evidence,
        guardrails=report,
    )
