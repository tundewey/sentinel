# Sentinel Project Gameplan

## Project Goal
Build and deploy a production-leaning AI incident intelligence platform by Friday using Alex-style architecture and workflow.

## MVP Outcomes
- Accept incident input
- Produce summary + severity + likely root cause + remediation steps
- Show structured dashboard output
- Deploy backend and frontend on AWS
- Add guardrails against prompt injection and unsupported claims

## Directory Structure

```
sentinel/
├── guides/
│   ├── 1_permissions.md
│   ├── 2_sagemaker.md
│   ├── 3_ingestion.md
│   ├── 4_intel.md
│   ├── 5_database.md
│   ├── 6_agents.md
│   ├── 7_frontend.md
│   ├── 8_enterprise.md
│   ├── architecture.md
│   └── agent_architecture.md
├── backend/
├── frontend/
├── terraform/
└── scripts/
```

## Execution Order
1. [1_permissions.md](guides/1_permissions.md)
2. [2_sagemaker.md](guides/2_sagemaker.md)
3. [3_ingestion.md](guides/3_ingestion.md)
4. [4_intel.md](guides/4_intel.md)
5. [5_database.md](guides/5_database.md)
6. [6_agents.md](guides/6_agents.md)
7. [7_frontend.md](guides/7_frontend.md)
8. [8_enterprise.md](guides/8_enterprise.md)

Also read:
- [architecture.md](guides/architecture.md)
- [agent_architecture.md](guides/agent_architecture.md)

## Guardrail Strategy
- Prompt injection detection/removal in Normalizer.
- Evidence extraction for grounding.
- Confidence-aware fallback when evidence is insufficient.
- Remediation output constrained to reversible, evidence-linked actions.

## Delivery Focus
- Ship a coherent vertical slice first.
- Keep cloud costs monitored daily.
- Prefer deterministic fallback behavior when model access is unavailable.
