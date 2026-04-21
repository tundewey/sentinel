"""Sentinel Intel service running on App Runner."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from common.heuristics import summarize_incident


app = FastAPI(title="Sentinel Intel", version="0.1.0")


class IntelRequest(BaseModel):
    text: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sentinel-intel"}


@app.post("/intel")
def intel(payload: IntelRequest) -> dict:
    summary = summarize_incident(payload.text)
    return {
        "summary": summary.summary,
        "severity": summary.severity,
        "severity_reason": summary.severity_reason,
    }
