function List({ items }) {
  if (!items || items.length === 0) return <p className="muted">No items</p>;
  return (
    <ul className="list">
      {items.map((item, index) => (
        <li key={`${index}-${item.slice(0, 10)}`}>{item}</li>
      ))}
    </ul>
  );
}

export default function AnalysisCards({ result }) {
  if (!result?.analysis) {
    return (
      <section className="card">
        <h2>Analysis Output</h2>
        <p className="muted">Submit an incident to view AI analysis.</p>
      </section>
    );
  }

  const { analysis } = result;

  return (
    <section className="stack gap">
      <article className="card">
        <h2>Summary</h2>
        <p>{analysis.summary.summary}</p>
        <p>
          <strong>Severity:</strong> <span className={`pill pill-${analysis.summary.severity}`}>{analysis.summary.severity}</span>
        </p>
        <p className="muted">{analysis.summary.severity_reason}</p>
      </article>

      <article className="card">
        <h2>Likely Root Cause</h2>
        <p><strong>{analysis.root_cause.likely_root_cause}</strong></p>
        <p>
          <strong>Confidence:</strong> {analysis.root_cause.confidence}
        </p>
        <p className="muted">{analysis.root_cause.reasoning}</p>
        <h3>Supporting Evidence</h3>
        <List items={analysis.root_cause.supporting_evidence} />
      </article>

      <article className="card">
        <h2>Recommended Next Actions</h2>
        <List items={analysis.remediation.recommended_actions} />
        <h3>Immediate Checks</h3>
        <List items={analysis.remediation.next_checks} />
        <p className="muted">
          <strong>Risk if unresolved:</strong> {analysis.remediation.risk_if_unresolved}
        </p>
      </article>

      <article className="card">
        <h2>Guardrails</h2>
        <p>
          Prompt injection detected: <strong>{analysis.guardrails.prompt_injection_detected ? "Yes" : "No"}</strong>
        </p>
        <p>Unsafe content removed: <strong>{analysis.guardrails.unsafe_content_removed ? "Yes" : "No"}</strong></p>
        <p>Input truncated: <strong>{analysis.guardrails.input_truncated ? "Yes" : "No"}</strong></p>
        {analysis.guardrails.notes?.length ? <List items={analysis.guardrails.notes} /> : null}
      </article>
    </section>
  );
}
