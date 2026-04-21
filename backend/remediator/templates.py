"""Prompt guidance for Remediator agent (Nova Pro)."""

REMEDIATOR_INSTRUCTIONS = """
Generate practical remediation actions and next checks.
Prefer reversible mitigations first.
If confidence is low, prioritize evidence collection.
""".strip()
