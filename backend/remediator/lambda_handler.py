"""Lambda handler for Remediator agent."""

from common.models import IncidentSummary, NormalizedIncident, RootCauseAnalysis
from remediator.agent import generate_remediation


def lambda_handler(event, context):
    normalized = NormalizedIncident.model_validate(event["normalized"])
    summary = IncidentSummary.model_validate(event["summary"])
    root_cause = RootCauseAnalysis.model_validate(event["root_cause"])
    result = generate_remediation(normalized, summary, root_cause)
    return result.model_dump()
