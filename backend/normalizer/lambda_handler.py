"""Lambda handler for Normalizer agent."""

from normalizer.agent import normalize_incident


def lambda_handler(event, context):
    text = event.get("text", "")
    result = normalize_incident(text)
    return result.model_dump()
