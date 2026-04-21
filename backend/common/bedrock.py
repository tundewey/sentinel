"""Bedrock helpers for optional model-backed analysis."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3

from common.config import bedrock_region, use_bedrock


logger = logging.getLogger(__name__)


def converse_json(model_id: str, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
    """Best-effort Bedrock Converse call that expects JSON output.

    Returns None when Bedrock is disabled or if invocation fails.
    """

    if not use_bedrock():
        return None

    try:
        client = boto3.client("bedrock-runtime", region_name=bedrock_region())
        response = client.converse(
            modelId=model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            inferenceConfig={"maxTokens": 700, "temperature": 0.1},
        )
        content = response["output"]["message"]["content"][0].get("text", "{}").strip()
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Bedrock converse failed; falling back to heuristics: %s", exc)
        return None
