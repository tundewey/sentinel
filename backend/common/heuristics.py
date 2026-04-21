"""Deterministic heuristics used when Bedrock is disabled or unavailable."""

from __future__ import annotations

import re

from common.models import Confidence, IncidentSummary, RemediationPlan, RootCauseAnalysis, Severity


def classify_severity(text: str) -> tuple[Severity, str]:
    """Rule-based severity from incident text."""

    t = text.lower()
    if re.search(r"(outage|sev1|critical|panic|fatal|service down|database down)", t):
        return "critical", "Detected outage/fatal indicators in the incident log."
    if re.search(r"(error|exception|timeout|timed out|503|500|failed|refused)", t):
        return "high", "Detected repeated runtime failures or availability issues."
    if re.search(r"(warn|degraded|retry|slow)", t):
        return "medium", "Detected warning/degradation patterns that can escalate."
    return "low", "No strong failure indicators detected in the supplied input."


def summarize_incident(text: str) -> IncidentSummary:
    """Generate concise incident summary and severity."""

    sev, reason = classify_severity(text)
    lines = [line.strip() for line in text.split("\n") if line.strip()][:4]
    headline = lines[0] if lines else "Incident input received with limited details."
    summary = (
        f"Incident indicates {sev} impact. Primary signal: {headline}. "
        f"Additional context lines reviewed: {max(len(lines) - 1, 0)}."
    )
    return IncidentSummary(summary=summary, severity=sev, severity_reason=reason)


def infer_root_cause(text: str, evidence: list[str]) -> RootCauseAnalysis:
    """Infer likely root cause from known patterns."""

    t = text.lower()
    if re.search(r"(access denied|unauthorized|forbidden|permission denied)", t):
        return RootCauseAnalysis(
            likely_root_cause="Authentication/authorization misconfiguration",
            confidence="high",
            reasoning="Logs show explicit auth or permission failure responses.",
            supporting_evidence=evidence[:3],
        )
    if re.search(r"(connection refused|could not connect|database unavailable|db timeout)", t):
        return RootCauseAnalysis(
            likely_root_cause="Database connectivity instability",
            confidence="high",
            reasoning="Connection errors indicate DB endpoint/network instability or resource exhaustion.",
            supporting_evidence=evidence[:3],
        )
    if re.search(r"(timeout|timed out|deadline exceeded)", t):
        return RootCauseAnalysis(
            likely_root_cause="Downstream service timeout/latency spike",
            confidence="medium",
            reasoning="Request timeout signatures suggest dependency latency or saturation.",
            supporting_evidence=evidence[:3],
        )
    if re.search(r"(oom|out of memory|killed process)", t):
        return RootCauseAnalysis(
            likely_root_cause="Memory pressure causing process instability",
            confidence="high",
            reasoning="OOM markers indicate memory limit breaches under workload.",
            supporting_evidence=evidence[:3],
        )
    if re.search(r"(throttl|rate limit|too many requests)", t):
        return RootCauseAnalysis(
            likely_root_cause="Rate limiting or quota exhaustion",
            confidence="medium",
            reasoning="Throttling signals indicate traffic beyond configured quotas.",
            supporting_evidence=evidence[:3],
        )
    return RootCauseAnalysis(
        likely_root_cause="Insufficient evidence to isolate one definitive root cause",
        confidence="low",
        reasoning="No dominant pattern was detected in the provided logs.",
        supporting_evidence=evidence[:3],
    )


def recommend_actions(root: RootCauseAnalysis, severity: Severity) -> RemediationPlan:
    """Generate pragmatic remediation based on root-cause classification."""

    cause = root.likely_root_cause.lower()
    actions: list[str] = []
    checks: list[str] = [
        "Correlate timestamps across application logs, infrastructure metrics, and recent deploy events.",
        "Confirm blast radius by checking error-rate and latency by service/endpoint.",
    ]

    if "auth" in cause or "permission" in cause:
        actions = [
            "Validate IAM/API auth configuration and rotate invalid credentials if needed.",
            "Re-run failed request with least-privilege test credentials.",
            "Add explicit auth failure alerts for early detection.",
        ]
    elif "database" in cause:
        actions = [
            "Validate database endpoint health, connection limits, and security-group rules.",
            "Temporarily increase connection pool timeout/backoff and retry jitter.",
            "Review recent DB changes and rollback if correlated to incident start.",
        ]
    elif "timeout" in cause or "latency" in cause:
        actions = [
            "Increase downstream timeout and circuit-breaker protection conservatively.",
            "Profile slow dependency path and cache high-latency calls.",
            "Scale impacted service tier and monitor p95/p99 latency recovery.",
        ]
    elif "memory" in cause:
        actions = [
            "Increase memory allocation for affected workload and restart unhealthy pods/functions.",
            "Inspect heap/object growth to identify leak candidates.",
            "Set memory saturation alerts before OOM thresholds.",
        ]
    elif "rate limiting" in cause or "quota" in cause:
        actions = [
            "Implement client backoff and request coalescing to reduce burst pressure.",
            "Request quota increase or shard traffic across regions/accounts as applicable.",
            "Introduce token-bucket controls at ingress to smooth spikes.",
        ]
    else:
        actions = [
            "Capture additional structured logs around the failing transaction path.",
            "Compare behavior against last known good release and config snapshot.",
            "Run focused replay in a staging environment to reproduce the failure deterministically.",
        ]

    risk = (
        "Critical customer impact likely to continue without immediate remediation."
        if severity == "critical"
        else "Service quality and reliability may degrade further if unresolved."
    )
    return RemediationPlan(recommended_actions=actions, next_checks=checks, risk_if_unresolved=risk)


def confidence_to_score(conf: Confidence) -> int:
    """Map confidence levels to integer for UI sorting/filters."""

    return {"low": 1, "medium": 2, "high": 3}[conf]
