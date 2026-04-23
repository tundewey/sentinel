"""Configuration helpers for Sentinel backend."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = str(BASE_DIR / "sentinel.db")


def get_db_path() -> str:
    return os.getenv("SENTINEL_DB_PATH", DEFAULT_DB_PATH)


def use_bedrock() -> bool:
    return os.getenv("ENABLE_BEDROCK", "false").lower() == "true"


def bedrock_region() -> str:
    return os.getenv("BEDROCK_REGION", os.getenv("DEFAULT_AWS_REGION", "eu-west-1"))


def model_support() -> str:
    return os.getenv("BEDROCK_MODEL_SUPPORT", "openai.gpt-oss-120b-1:0")


def model_root_cause() -> str:
    return os.getenv("BEDROCK_MODEL_ROOT_CAUSE", "eu.amazon.nova-pro-v1:0")


def model_remediation() -> str:
    return os.getenv("BEDROCK_MODEL_REMEDIATION", "eu.amazon.nova-pro-v1:0")
