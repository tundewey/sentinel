"""Lambda handler for Investigator agent."""

from common.models import IncidentSummary, NormalizedIncident
from investigator.agent import investigate_root_cause


def lambda_handler(event, context):
    normalized = NormalizedIncident.model_validate(event["normalized"])
    summary = IncidentSummary.model_validate(event["summary"])
    result = investigate_root_cause(normalized, summary)
    return result.model_dump()
