"""Guardrails for prompt injection and grounded responses."""

from __future__ import annotations

import re

from common.models import GuardrailReport, RemediationPlan, RootCauseAnalysis


DANGEROUS_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"disregard\s+all\s+prior",
    r"forget\s+everything",
    r"new\s+instructions\s*:",
    r"^system\s*:",
    r"^assistant\s*:",
    r"<\s*tool\s*>",
    r"prompt\s*injection",
]

EVIDENCE_HINTS = re.compile(
    r"(error|exception|traceback|timeout|timed\s*out|denied|failed|refused|503|500|panic|oom|throttl)",
    re.IGNORECASE,
)


def sanitize_incident_text(text: str, max_chars: int = 12000) -> tuple[str, GuardrailReport]:
    """Sanitize input text and remove likely prompt-injection lines."""

    report = GuardrailReport()
    clean = text.replace("\x00", " ").replace("\r", "")

    if len(clean) > max_chars:
        clean = clean[:max_chars]
        report.input_truncated = True
        report.notes.append(f"Input truncated to {max_chars} characters.")

    kept_lines: list[str] = []
    for line in clean.split("\n"):
        line_stripped = line.strip()
        blocked = False
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                report.prompt_injection_detected = True
                report.blocked_patterns.append(pattern)
                blocked = True
                break
        if not blocked:
            kept_lines.append(line)

    if report.prompt_injection_detected:
        report.unsafe_content_removed = True
        report.notes.append("Potential prompt-injection fragments removed from incident input.")

    sanitized = "\n".join(kept_lines).strip()
    if not sanitized:
        sanitized = "[EMPTY_AFTER_SANITIZATION]"
        report.notes.append("Input became empty after sanitization.")

    return sanitized, report


def extract_evidence_snippets(text: str, max_snippets: int = 6) -> list[str]:
    """Extract evidence-like log lines to ground downstream reasoning."""

    snippets: list[str] = []
    for line in text.split("\n"):
        candidate = line.strip()
        if not candidate:
            continue
        if EVIDENCE_HINTS.search(candidate):
            snippets.append(candidate[:300])
        if len(snippets) >= max_snippets:
            return snippets

    if not snippets:
        fallback = [line.strip()[:300] for line in text.split("\n") if line.strip()][:3]
        snippets.extend(fallback)

    return snippets


def enforce_grounding(
    root_cause: RootCauseAnalysis,
    remediation: RemediationPlan,
    evidence_snippets: list[str],
) -> tuple[RootCauseAnalysis, RemediationPlan]:
    """Prevent unsupported claims by forcing evidence-aware outputs."""

    if not evidence_snippets:
        root_cause.likely_root_cause = "Insufficient evidence to determine a root cause."
        root_cause.confidence = "low"
        root_cause.reasoning = "No concrete error lines were provided in the incident payload."
        root_cause.supporting_evidence = ["No evidence snippets available"]

    if root_cause.confidence == "low":
        guardrail_action = "Collect additional logs and metrics before applying irreversible fixes."
        if guardrail_action not in remediation.recommended_actions:
            remediation.recommended_actions.insert(0, guardrail_action)

    if not root_cause.supporting_evidence:
        root_cause.supporting_evidence = evidence_snippets[:3] or ["No supporting evidence extracted"]

    return root_cause, remediation
