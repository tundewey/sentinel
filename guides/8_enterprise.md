# Guide 8 - Enterprise Hardening

## Objective
Enable operational dashboards, alarms, and safety checks.

## Deploy Monitoring Stack
```bash
cd terraform/8_enterprise
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Verify
- CloudWatch dashboard exists.
- Alarm subscriptions are confirmed.
- API and planner error alarms are active.
- SQS queue age alarm is active.

## Recommended Guardrails
- Keep prompt-injection filtering enabled.
- Require evidence snippets before high-confidence claims.
- Log confidence and guardrail flags for every analysis.
- Add allow-list validation for external tool calls.

## Cost Discipline
Use `uv run scripts/check_costs.py` daily and destroy stacks when idle.
