"""Schema placeholders for Sentinel DB-centric workflows."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IncidentRecord(BaseModel):
    incident_id: str
    title: str | None = Field(default=None)
    source: str
    created_at: str
