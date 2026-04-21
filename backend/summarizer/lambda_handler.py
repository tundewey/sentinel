"""Lambda handler for Summarizer agent."""

from common.models import NormalizedIncident
from summarizer.agent import summarize_incident


def lambda_handler(event, context):
    normalized = NormalizedIncident.model_validate(event["normalized"])
    result = summarize_incident(normalized)
    return result.model_dump()
