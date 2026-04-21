"""Orchestration pipeline shared by API and planner lambda."""

from __future__ import annotations

import json

from common.config import get_db_path, model_remediation, model_root_cause, model_support
from common.models import IncidentAnalysis, IncidentInput, JobRunResponse
from common.store import Database
from investigator.agent import investigate_root_cause
from normalizer.agent import normalize_incident
from remediator.agent import generate_remediation
from summarizer.agent import summarize_incident


def run_job(job_id: str, db: Database | None = None, clerk_user_id: str | None = None) -> JobRunResponse:
    """Execute the full multi-agent workflow for one job."""

    owned_db = False
    if db is None:
        db = Database(get_db_path())
        owned_db = True

    try:
        row = db.get_job_with_incident(job_id, clerk_user_id=clerk_user_id)
        if not row:
            return JobRunResponse(incident_id="", job_id=job_id, status="failed", error="Job not found")

        db.update_job_status(job_id, "processing")

        normalized = normalize_incident(row["raw_text"])
        db.update_incident_sanitization(
            row["incident_id"],
            normalized.normalized_text,
            normalized.guardrails.model_dump(),
        )

        summary = summarize_incident(normalized)
        root_cause = investigate_root_cause(normalized, summary)
        remediation = generate_remediation(normalized, summary, root_cause)

        analysis = IncidentAnalysis(
            incident_id=row["incident_id"],
            job_id=job_id,
            summary=summary,
            root_cause=root_cause,
            remediation=remediation,
            guardrails=normalized.guardrails,
            models={
                "support": model_support(),
                "root_cause": model_root_cause(),
                "remediation": model_remediation(),
            },
        )

        db.save_analysis(job_id, analysis)
        return JobRunResponse(incident_id=row["incident_id"], job_id=job_id, status="completed", analysis=analysis)

    except Exception as exc:  # noqa: BLE001
        db.update_job_status(job_id, "failed", str(exc))
        row = db.get_job(job_id, clerk_user_id=clerk_user_id) or {"incident_id": ""}
        return JobRunResponse(
            incident_id=row.get("incident_id", ""),
            job_id=job_id,
            status="failed",
            error=str(exc),
        )
    finally:
        if owned_db:
            db.close()


def create_incident_and_job(
    payload: IncidentInput,
    db: Database | None = None,
    clerk_user_id: str = "anonymous",
) -> tuple[str, str]:
    """Create incident/job records in pending state."""

    owned_db = False
    if db is None:
        db = Database(get_db_path())
        owned_db = True

    try:
        incident_id = db.create_incident(
            text=payload.text,
            title=payload.title,
            source=payload.source,
            clerk_user_id=clerk_user_id,
        )
        job_id = db.create_job(incident_id=incident_id, clerk_user_id=clerk_user_id)
        return incident_id, job_id
    finally:
        if owned_db:
            db.close()


def parse_analysis(job_row: dict) -> dict | None:
    """Parse analysis payload from DB row."""

    raw = job_row.get("analysis_json")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
