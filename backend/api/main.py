"""Sentinel API service."""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.auth import AuthContext, require_auth
from common.config import get_db_path
from common.models import IncidentInput, JobCreateResponse
from common.pipeline import create_incident_and_job, parse_analysis, run_job
from common.store import Database


app = FastAPI(title="Sentinel API", version="0.3.0")

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _db() -> Database:
    return Database(get_db_path())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sentinel-api"}


@app.get("/api/me")
def me(user: AuthContext = Depends(require_auth)) -> dict[str, Any]:
    return {"user_id": user.user_id, "email": user.email}


@app.post("/api/incidents", response_model=JobCreateResponse)
def create_incident(payload: IncidentInput, user: AuthContext = Depends(require_auth)) -> JobCreateResponse:
    db = _db()
    try:
        incident_id, job_id = create_incident_and_job(payload, db, clerk_user_id=user.user_id)
        return JobCreateResponse(incident_id=incident_id, job_id=job_id, status="pending")
    finally:
        db.close()


@app.post("/api/incidents/analyze-sync")
def analyze_sync(payload: IncidentInput, user: AuthContext = Depends(require_auth)) -> dict[str, Any]:
    db = _db()
    try:
        incident_id, job_id = create_incident_and_job(payload, db, clerk_user_id=user.user_id)
        result = run_job(job_id, db, clerk_user_id=user.user_id)
        return result.model_dump()
    finally:
        db.close()


@app.post("/api/jobs/{job_id}/run")
def run_analysis(job_id: str, user: AuthContext = Depends(require_auth)) -> dict[str, Any]:
    db = _db()
    try:
        row = db.get_job(job_id, clerk_user_id=user.user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        result = run_job(job_id, db, clerk_user_id=user.user_id)
        return result.model_dump()
    finally:
        db.close()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, user: AuthContext = Depends(require_auth)) -> dict[str, Any]:
    db = _db()
    try:
        row = db.get_job(job_id, clerk_user_id=user.user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "job_id": row["id"],
            "incident_id": row["incident_id"],
            "status": row["status"],
            "error": row.get("error_message"),
            "analysis": parse_analysis(row),
        }
    finally:
        db.close()


@app.get("/api/incidents")
def list_incidents(limit: int = 25, user: AuthContext = Depends(require_auth)) -> list[dict[str, Any]]:
    db = _db()
    try:
        incidents = db.list_incidents(limit=limit, clerk_user_id=user.user_id)
        out: list[dict[str, Any]] = []
        for row in incidents:
            guard = {}
            if row.get("guardrail_json"):
                try:
                    guard = json.loads(row["guardrail_json"])
                except json.JSONDecodeError:
                    guard = {}
            out.append(
                {
                    "incident_id": row["id"],
                    "title": row.get("title"),
                    "source": row["source"],
                    "created_at": row["created_at"],
                    "guardrails": guard,
                }
            )
        return out
    finally:
        db.close()
