"""Prompt guidance for Planner orchestrator."""

PLANNER_INSTRUCTIONS = """
Orchestrate Normalizer -> Summarizer -> Investigator -> Remediator.
Persist results and fail safely with clear error messages.
""".strip()
