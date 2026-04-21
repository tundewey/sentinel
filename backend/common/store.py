"""SQLite persistence layer for Sentinel MVP local and lambda testing."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

from common.models import IncidentAnalysis


class Database:
    """Lightweight database wrapper for incidents and analysis jobs."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                  id TEXT PRIMARY KEY,
                  clerk_user_id TEXT NOT NULL DEFAULT 'anonymous',
                  title TEXT,
                  source TEXT NOT NULL,
                  raw_text TEXT NOT NULL,
                  sanitized_text TEXT,
                  guardrail_json TEXT,
                  created_at TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                  id TEXT PRIMARY KEY,
                  incident_id TEXT NOT NULL,
                  clerk_user_id TEXT NOT NULL DEFAULT 'anonymous',
                  status TEXT NOT NULL,
                  error_message TEXT,
                  analysis_json TEXT,
                  created_at TEXT NOT NULL,
                  completed_at TEXT,
                  FOREIGN KEY (incident_id) REFERENCES incidents(id)
                )
                """
            )
            self._ensure_column("incidents", "clerk_user_id", "TEXT NOT NULL DEFAULT 'anonymous'")
            self._ensure_column("jobs", "clerk_user_id", "TEXT NOT NULL DEFAULT 'anonymous'")

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        cols = [row["name"] for row in self._conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def create_incident(
        self,
        text: str,
        title: str | None,
        source: str,
        clerk_user_id: str,
        sanitized_text: str | None = None,
        guardrail_json: dict | None = None,
    ) -> str:
        incident_id = str(uuid.uuid4())
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO incidents (id, clerk_user_id, title, source, raw_text, sanitized_text, guardrail_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    clerk_user_id,
                    title,
                    source,
                    text,
                    sanitized_text,
                    json.dumps(guardrail_json or {}),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return incident_id

    def update_incident_sanitization(self, incident_id: str, sanitized_text: str, guardrail_json: dict) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE incidents SET sanitized_text=?, guardrail_json=? WHERE id=?",
                (sanitized_text, json.dumps(guardrail_json), incident_id),
            )

    def create_job(self, incident_id: str, clerk_user_id: str, status: str = "pending") -> str:
        job_id = str(uuid.uuid4())
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO jobs (id, incident_id, clerk_user_id, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_id, incident_id, clerk_user_id, status, datetime.now(timezone.utc).isoformat()),
            )
        return job_id

    def update_job_status(self, job_id: str, status: str, error_message: str | None = None) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE jobs SET status=?, error_message=? WHERE id=?",
                (status, error_message, job_id),
            )

    def save_analysis(self, job_id: str, analysis: IncidentAnalysis) -> None:
        with self._conn:
            self._conn.execute(
                """
                UPDATE jobs
                SET status='completed', analysis_json=?, completed_at=?
                WHERE id=?
                """,
                (
                    analysis.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                    job_id,
                ),
            )

    def get_incident(self, incident_id: str, clerk_user_id: str | None = None) -> dict | None:
        if clerk_user_id:
            row = self._conn.execute(
                "SELECT * FROM incidents WHERE id=? AND clerk_user_id=?",
                (incident_id, clerk_user_id),
            ).fetchone()
        else:
            row = self._conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
        return dict(row) if row else None

    def list_incidents(self, limit: int = 50, clerk_user_id: str | None = None) -> list[dict]:
        if clerk_user_id:
            rows = self._conn.execute(
                "SELECT * FROM incidents WHERE clerk_user_id=? ORDER BY created_at DESC LIMIT ?",
                (clerk_user_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_job(self, job_id: str, clerk_user_id: str | None = None) -> dict | None:
        if clerk_user_id:
            row = self._conn.execute(
                "SELECT * FROM jobs WHERE id=? AND clerk_user_id=?",
                (job_id, clerk_user_id),
            ).fetchone()
        else:
            row = self._conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    def get_job_with_incident(self, job_id: str, clerk_user_id: str | None = None) -> dict | None:
        if clerk_user_id:
            row = self._conn.execute(
                """
                SELECT j.*, i.raw_text, i.title, i.source, i.sanitized_text, i.guardrail_json
                FROM jobs j
                JOIN incidents i ON i.id = j.incident_id
                WHERE j.id = ? AND j.clerk_user_id = ?
                """,
                (job_id, clerk_user_id),
            ).fetchone()
        else:
            row = self._conn.execute(
                """
                SELECT j.*, i.raw_text, i.title, i.source, i.sanitized_text, i.guardrail_json
                FROM jobs j
                JOIN incidents i ON i.id = j.incident_id
                WHERE j.id = ?
                """,
                (job_id,),
            ).fetchone()
        return dict(row) if row else None

    def close(self) -> None:
        self._conn.close()
