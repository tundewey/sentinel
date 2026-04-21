"""Planner orchestrator agent."""

from __future__ import annotations

from common.models import IncidentInput, JobRunResponse
from common.pipeline import create_incident_and_job, run_job
from common.store import Database


def create_and_run(payload: IncidentInput, db: Database) -> JobRunResponse:
    """Create incident/job and execute analysis immediately."""

    incident_id, job_id = create_incident_and_job(payload, db)
    result = run_job(job_id, db)
    result.incident_id = incident_id
    return result
