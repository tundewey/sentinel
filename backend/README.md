# Sentinel Backend

## Core Services
- `api`: FastAPI API for incident intake and analysis retrieval
- `ingest`: Lambda for API-key protected ingestion flows
- `intel`: App Runner supporting intelligence service
- `database`: utilities for local schema reset/seed/verify
- `planner`, `normalizer`, `summarizer`, `investigator`, `remediator`: incident agent orchestra

## Guardrails
- Prompt-injection pattern stripping in `normalizer`
- Evidence extraction before root-cause inference
- Confidence-aware fallback for weak evidence
- Remediation constrained by evidence confidence

## Quick Validation
```bash
uv run test_simple.py
uv run test_full.py
uv run package_docker.py --include-api --include-ingest
```
