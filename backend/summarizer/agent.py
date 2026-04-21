"""Summarizer agent implementation."""

from __future__ import annotations

from common.heuristics import summarize_incident as heuristic_summarize
from common.models import IncidentSummary, NormalizedIncident


def summarize_incident(normalized: NormalizedIncident) -> IncidentSummary:
    """Create incident summary and severity."""

    return heuristic_summarize(normalized.normalized_text)
