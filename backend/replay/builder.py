from __future__ import annotations

from copy import deepcopy
from typing import Any

from common.models import ReplayFrame, ReplayResponse


_STAGE_TITLE = {
    "queued": "Queued",
    "normalize": "Normalize",
    "summarize": "Summarize",
    "root_cause": "Root Cause",
    "remediate": "Remediate",
    "completed": "Completed",
    "failed": "Failed",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _normalize_stage(stage: str) -> str:
    s = (stage or "").strip().lower()
    aliases = {
        "root-cause": "root_cause",
        "rootcause": "root_cause",
        "done": "completed",
    }
    return aliases.get(s, s)


def _json_equal(a: Any, b: Any) -> bool:
    return a == b


def _compute_delta(prev: dict[str, Any], curr: dict[str, Any]) -> dict[str, Any]:
    delta: dict[str, Any] = {}
    keys = set(prev.keys()) | set(curr.keys())
    for k in sorted(keys):
        pv = prev.get(k)
        cv = curr.get(k)
        if not _json_equal(pv, cv):
            delta[k] = {"from": pv, "to": cv}
    return delta


def _snapshot_for_stage(
    stage: str,
    workflow: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    job = _as_dict(workflow.get("job"))
    analysis = _as_dict(workflow.get("analysis"))
    summary = _as_dict(analysis.get("summary"))
    root_cause = _as_dict(analysis.get("root_cause"))
    remediation = _as_dict(analysis.get("remediation"))
    guardrails = _as_dict(analysis.get("guardrails"))
    actions = _as_list(workflow.get("remediation_actions"))
    pir = _as_dict(workflow.get("post_incident_review"))
    incident = _as_dict(workflow.get("incident"))

    normalized_text = str(workflow.get("normalized_text") or "")
    norm_preview = normalized_text[:280] + ("..." if len(normalized_text) > 280 else "")

    snap: dict[str, Any] = {
        "job_status": job.get("status"),
        "current_stage": stage,
        "detail": event.get("detail") or "",
    }

    if stage == "queued":
        snap.update(
            {
                "incident_id": job.get("incident_id"),
                "title": incident.get("title"),
                "source": incident.get("source"),
            }
        )
    elif stage == "normalize":
        snap.update(
            {
                "normalized_text_preview": norm_preview,
                "evidence_count": len(_as_list(guardrails.get("notes"))),  # conservative proxy
                "guardrails": {
                    "prompt_injection_detected": guardrails.get("prompt_injection_detected"),
                    "unsafe_content_removed": guardrails.get("unsafe_content_removed"),
                    "input_truncated": guardrails.get("input_truncated"),
                },
            }
        )
    elif stage == "summarize":
        snap.update(
            {
                "summary": summary.get("summary"),
                "severity": summary.get("severity"),
                "severity_reason": summary.get("severity_reason"),
            }
        )
    elif stage == "root_cause":
        snap.update(
            {
                "likely_root_cause": root_cause.get("likely_root_cause"),
                "confidence": root_cause.get("confidence"),
                "supporting_evidence_count": len(_as_list(root_cause.get("supporting_evidence"))),
            }
        )
    elif stage == "remediate":
        snap.update(
            {
                "recommended_actions_count": len(_as_list(remediation.get("recommended_actions"))),
                "next_checks_count": len(_as_list(remediation.get("next_checks"))),
                "risk_if_unresolved": remediation.get("risk_if_unresolved"),
                "open_action_items": len([a for a in actions if (a.get("status") or "").lower() != "done"]),
            }
        )
    elif stage == "completed":
        snap.update(
            {
                "completed_at": job.get("completed_at"),
                "pir_present": bool(pir),
                "total_actions": len(actions),
                "done_actions": len([a for a in actions if (a.get("status") or "").lower() == "done"]),
            }
        )
    elif stage == "failed":
        snap.update(
            {
                "error": job.get("error"),
            }
        )

    return snap


def build_replay(workflow: dict[str, Any]) -> ReplayResponse:
    job = _as_dict(workflow.get("job"))
    events = _as_list(workflow.get("pipeline_events"))

    frames: list[ReplayFrame] = []
    prev_snapshot: dict[str, Any] = {}

    if not events:
        stage = _normalize_stage(str(job.get("current_stage") or "queued"))
        synthetic_event = {"stage": stage, "detail": "No pipeline events recorded", "at": job.get("created_at")}
        snap = _snapshot_for_stage(stage, workflow, synthetic_event)
        frames.append(
            ReplayFrame(
                index=0,
                stage=stage if stage in _STAGE_TITLE else "queued",
                title=_STAGE_TITLE.get(stage, "Queued"),
                at=synthetic_event.get("at"),
                detail=synthetic_event.get("detail"),
                snapshot=snap,
                delta=_compute_delta({}, snap),
            )
        )
    else:
        for i, ev in enumerate(events):
            raw_stage = str(_as_dict(ev).get("stage") or "")
            stage = _normalize_stage(raw_stage)
            if stage not in _STAGE_TITLE:
                stage = "queued"
            snap = _snapshot_for_stage(stage, workflow, _as_dict(ev))
            delta = _compute_delta(prev_snapshot, snap)
            frames.append(
                ReplayFrame(
                    index=i,
                    stage=stage,  # type: ignore[arg-type]
                    title=_STAGE_TITLE[stage],
                    at=_as_dict(ev).get("at"),
                    detail=_as_dict(ev).get("detail"),
                    snapshot=deepcopy(snap),
                    delta=delta,
                )
            )
            prev_snapshot = snap

    return ReplayResponse(
        job_id=str(job.get("job_id") or ""),
        status=str(job.get("status") or ""),
        started_at=job.get("created_at"),
        completed_at=job.get("completed_at"),
        frames=frames,
    )