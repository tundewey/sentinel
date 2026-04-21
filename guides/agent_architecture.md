# Sentinel Agent Architecture

## Agent Roles
- **Planner**: orchestration and persistence lifecycle
- **Normalizer**: sanitization, prompt-injection filtering, evidence extraction
- **Summarizer**: concise summary + severity classification
- **Investigator**: likely root-cause analysis (Nova Pro)
- **Remediator**: prioritized next actions (Nova Pro)

## Sequence
```mermaid
sequenceDiagram
    participant U as User/API
    participant P as Planner
    participant N as Normalizer
    participant S as Summarizer
    participant I as Investigator
    participant R as Remediator
    participant DB as Aurora

    U->>P: Analyze job_id
    P->>DB: Load incident
    P->>N: Normalize + guardrails
    N-->>P: sanitized_text + evidence + guardrail flags
    P->>S: Summarize + severity
    S-->>P: summary
    P->>I: Root cause request
    I-->>P: likely cause + confidence + evidence links
    P->>R: Remediation request
    R-->>P: actions + checks + risk
    P->>DB: Store final analysis
```

## Guardrails
- Injection patterns are blocked before model analysis.
- Weak evidence forces low-confidence response.
- Remediation is constrained to observable/reversible steps.
