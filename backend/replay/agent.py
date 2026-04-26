from __future__ import annotations

import json
from typing import Any

from common.bedrock import converse_json
from common.models import ReplayExplainResponse
from replay.templates import REPLAY_EXPLAIN_SYSTEM


def _compact_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    job = workflow.get("job") or {}
    analysis = workflow.get("analysis") or {}
    return {
        "job": {
            "job_id": job.get("job_id"),
            "status": job.get("status"),
            "current_stage": job.get("current_stage"),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at"),
        },
        "analysis": {
            "summary": (analysis.get("summary") or {}).get("summary"),
            "severity": (analysis.get("summary") or {}).get("severity"),
            "root_cause": (analysis.get("root_cause") or {}).get("likely_root_cause"),
            "risk_if_unresolved": (analysis.get("remediation") or {}).get("risk_if_unresolved"),
        },
    }


def explain_replay_frame(
    workflow: dict[str, Any],
    frame: dict[str, Any],
    frame_index: int,
) -> ReplayExplainResponse:
    prompt = (
        "Explain this replay frame.\n\n"
        f"Frame index: {frame_index}\n"
        f"Frame:\n{json.dumps(frame, default=str)}\n\n"
        f"Workflow context:\n{json.dumps(_compact_workflow(workflow), default=str)}"
    )

    result = converse_json(REPLAY_EXPLAIN_SYSTEM, prompt, max_tokens=900)

    if not result:
        return ReplayExplainResponse(
            frame_index=frame_index,
            explanation="I could not generate a grounded explanation for this replay step.",
            confidence="low",
            evidence=[],
        )

    try:
        return ReplayExplainResponse(
            frame_index=frame_index,
            explanation=str(result.get("explanation") or "").strip()
            or "No explanation returned.",
            confidence=str(result.get("confidence") or "low"),  # validated by Pydantic
            evidence=list(result.get("evidence") or []),
        )
    except Exception:
        return ReplayExplainResponse(
            frame_index=frame_index,
            explanation="The model response could not be parsed for this frame.",
            confidence="low",
            evidence=[],
        )