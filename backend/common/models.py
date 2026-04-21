"""Pydantic models for Sentinel incident intelligence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]
Confidence = Literal["low", "medium", "high"]


class IncidentInput(BaseModel):
    """Incident/log payload from UI or API callers."""

    text: str = Field(min_length=1, max_length=50000)
    title: str | None = Field(default=None, max_length=200)
    source: str = Field(default="manual", max_length=100)


class GuardrailReport(BaseModel):
    """Guardrail status for one incident run."""

    prompt_injection_detected: bool = False
    blocked_patterns: list[str] = Field(default_factory=list)
    input_truncated: bool = False
    unsafe_content_removed: bool = False
    notes: list[str] = Field(default_factory=list)


class NormalizedIncident(BaseModel):
    """Sanitized incident with extracted evidence snippets."""

    normalized_text: str
    evidence_snippets: list[str] = Field(default_factory=list)
    guardrails: GuardrailReport


class IncidentSummary(BaseModel):
    """Summary and severity classification."""

    summary: str
    severity: Severity
    severity_reason: str


class RootCauseAnalysis(BaseModel):
    """Likely root cause with confidence and rationale."""

    likely_root_cause: str
    confidence: Confidence
    reasoning: str
    supporting_evidence: list[str] = Field(default_factory=list)


class RemediationPlan(BaseModel):
    """Recommended actions and immediate checks."""

    recommended_actions: list[str] = Field(default_factory=list)
    next_checks: list[str] = Field(default_factory=list)
    risk_if_unresolved: str


class IncidentAnalysis(BaseModel):
    """Combined output from all agents."""

    incident_id: str
    job_id: str
    summary: IncidentSummary
    root_cause: RootCauseAnalysis
    remediation: RemediationPlan
    guardrails: GuardrailReport
    models: dict[str, str]
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class JobCreateResponse(BaseModel):
    """Response when creating a pending job."""

    incident_id: str
    job_id: str
    status: str


class JobRunResponse(BaseModel):
    """Response when running analysis."""

    incident_id: str
    job_id: str
    status: str
    analysis: IncidentAnalysis | None = None
    error: str | None = None
