# Sentinel Architecture Overview

```mermaid
graph TB
    User[Operator] --> Web[CloudFront + Next.js UI]
    Web --> APIG[API Gateway]
    APIG --> API[Lambda API]

    API --> SQS[SQS Jobs]
    SQS --> Planner[Planner Lambda]

    Planner --> Normalizer[Normalizer Lambda]
    Planner --> Summarizer[Summarizer Lambda]
    Planner --> Investigator[Investigator Lambda - Nova Pro]
    Planner --> Remediator[Remediator Lambda - Nova Pro]

    API --> Aurora[(Aurora Serverless v2)]
    Planner --> Aurora

    Intel[App Runner Intel Service] --> Bedrock2[Bedrock GPT OSS 120B]
    Planner --> Bedrock1[Bedrock Nova Pro]

    Ingest[Ingest Lambda] --> APIG
```

## Notes
- API writes incidents and jobs.
- Planner orchestrates all analysis steps.
- Normalizer enforces guardrails first.
- Aurora stores incidents, jobs, and analysis payloads.
- Intel service handles supporting analysis workflows.
