# Sentinel Agent Project Instructions

This repository follows Alex-style patterns for rapid production delivery.

## Rules
- Use `uv` for Python package management and script execution.
- Prefer incremental diagnosis before broad code changes.
- Keep terraform directories independent with local state.
- Use Nova Pro for root-cause and remediation agents.
- Use GPT OSS 120B for non-critical/supporting analysis where appropriate.

## Backend Agent Modules
- `planner`: orchestrates incident analysis flow
- `normalizer`: cleans and structures incident/log input
- `summarizer`: produces concise incident narratives
- `investigator`: identifies likely root cause (Nova Pro)
- `remediator`: proposes next actions/remediation (Nova Pro)
