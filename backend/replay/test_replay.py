from replay.builder import build_replay


def test_build_replay_from_workflow_events():
    wf = {
        "job": {
            "job_id": "j1",
            "status": "completed",
            "incident_id": "i1",
            "created_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:01:00Z",
            "current_stage": "completed",
        },
        "pipeline_events": [
            {"stage": "queued", "detail": "Starting pipeline", "at": "2026-01-01T00:00:00Z"},
            {"stage": "summarize", "detail": "Generating summary", "at": "2026-01-01T00:00:10Z"},
            {"stage": "completed", "detail": "Analysis ready", "at": "2026-01-01T00:01:00Z"},
        ],
        "analysis": {
            "summary": {"summary": "S", "severity": "high", "severity_reason": "R"},
            "root_cause": {"likely_root_cause": "DB", "confidence": "high", "supporting_evidence": []},
            "remediation": {"recommended_actions": [], "next_checks": [], "risk_if_unresolved": "X"},
            "guardrails": {},
        },
        "remediation_actions": [],
        "post_incident_review": {},
        "incident": {"title": "Incident"},
        "normalized_text": "sample",
    }
    replay = build_replay(wf)
    assert replay.job_id == "j1"
    assert len(replay.frames) == 3
    assert replay.frames[0].stage == "queued"
    assert replay.frames[-1].stage == "completed"