import RunTimeline from "./RunTimeline";

function formatWhen(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function Section({ title, children, id }) {
  return (
    <section className="card-elevated audit-section" id={id} style={{ marginBottom: 20, padding: "20px 24px" }}>
      <h2 className="run-title" style={{ margin: "0 0 12px", fontSize: "0.95rem" }}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function KeyValueList({ items }) {
  return (
    <dl className="audit-kv">
      {items.map(({ k, v }) => (
        <div key={k} className="audit-kv-row">
          <dt className="muted small">{k}</dt>
          <dd>{v ?? "—"}</dd>
        </div>
      ))}
    </dl>
  );
}

function TextBlock({ text }) {
  if (text == null || text === "") return <p className="muted small">—</p>;
  return <div className="audit-prose">{text}</div>;
}

/** Audit trail labels: nested checklist items vs. clarification Q&A vs. engineer-added follow-up actions. */
function AuditBadge({ variant, children }) {
  return <span className={`audit-badge audit-badge--${variant}`}>{children}</span>;
}

/** Map DB action_type + trail context to professional labels (not raw snake_case). */
function buildActionIndex(actions) {
  const m = {};
  for (const a of actions) {
    m[a.id] = a;
  }
  return m;
}

function actionKind(action, byId) {
  const raw = (action.action_type || "recommended").toLowerCase();
  if (raw === "trail") {
    const parent = action.parent_action_id ? byId[action.parent_action_id] : null;
    const pt = (parent?.action_type || "").toLowerCase();
    if (pt === "check" || pt === "followup_check") {
      return { title: "Sub-step", subtitle: "Under a verification check" };
    }
    if (pt === "followup") {
      return { title: "Sub-step", subtitle: "Under a follow-up action" };
    }
    return { title: "Sub-step", subtitle: "Under a remediation to-do" };
  }
  const map = {
    recommended: { title: "Remediation to-do", subtitle: "Primary plan item" },
    check: { title: "Verification check", subtitle: "Immediate check" },
    followup: { title: "Follow-up action", subtitle: "After engineer findings" },
    followup_check: { title: "Follow-up verification", subtitle: "Check from follow-up" },
  };
  if (map[raw]) return map[raw];
  return {
    title: raw.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    subtitle: "",
  };
}

function formatStatus(s) {
  if (s == null || s === "") return "—";
  const k = String(s).toLowerCase();
  const labels = { pending: "Pending", done: "Done", skipped: "Skipped", open: "Open", resolved: "Resolved", in_progress: "In progress" };
  return labels[k] || s.charAt(0).toUpperCase() + s.slice(1);
}

function formatSeverity(s) {
  if (s == null || s === "") return "—";
  const k = String(s).toLowerCase();
  return k.charAt(0).toUpperCase() + k.slice(1);
}

function formatChatRole(role) {
  const r = String(role || "").toLowerCase();
  if (r === "user") return "User";
  if (r === "assistant") return "Assistant";
  return role ? String(role).replace(/\b\w/g, (c) => c.toUpperCase()) : "—";
}

function formatPipelineStageId(id) {
  if (id == null || id === "") return "—";
  return String(id)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function truncate(s, n) {
  if (s == null) return "";
  const t = String(s);
  if (t.length <= n) return t;
  return `${t.slice(0, n)}…`;
}

function formatQuestionKind(k) {
  if (k == null || k === "") return "";
  const s = String(k).toLowerCase();
  if (s === "yes_no") return "Yes / no";
  if (s === "text") return "Text";
  if (s === "choice") return "Choice";
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Root actions by plan type; rows with `parent_action_id` are nested sub-steps (any type). */
const CHECKLIST_GROUPS = [
  {
    id: "remediation",
    title: "Remediation to-do",
    blurb: "Primary plan items from the initial or refined remediation.",
  },
  {
    id: "verification",
    title: "Verification checks",
    blurb: "Immediate verification steps from the plan.",
  },
  {
    id: "followup",
    title: "Follow-up actions",
    blurb: "Added after engineer-reported findings.",
  },
  {
    id: "followup_verification",
    title: "Follow-up verifications",
    blurb: "Checks generated in the follow-up flow.",
  },
  {
    id: "substep",
    title: "Sub-steps (unlinked)",
    blurb: "Rows whose parent is missing from this export (rare). Otherwise sub-steps are nested under the parent in each section above.",
  },
  {
    id: "other",
    title: "Other",
    blurb: null,
  },
];

function buildParentChildrenMap(actions) {
  const byId = buildActionIndex(actions);
  const byParent = new Map();
  for (const a of actions) {
    const pid = a.parent_action_id || null;
    if (!byParent.has(pid)) byParent.set(pid, []);
    byParent.get(pid).push(a);
  }
  for (const arr of byParent.values()) {
    arr.sort((a, b) => (a.created_at || "").localeCompare(b.created_at || ""));
  }
  return { byId, byParent };
}

/**
 * Tree walk from a top-level root: parent first, then descendants in depth-first order
 * (matches “parent remediation + children” in one block).
 */
function walkActionSubtrees(root, byParent) {
  const out = [];
  function visit(node, depth) {
    out.push({ action: node, depth });
    for (const ch of (byParent.get(node.id) || [])) {
      visit(ch, depth + 1);
    }
  }
  visit(root, 0);
  return out;
}

function rootOrderInActions(actions) {
  const order = new Map();
  actions.forEach((a, i) => order.set(a.id, i));
  return order;
}

function isRootNode(a) {
  return !a.parent_action_id;
}

function rootMatchesGroup(a, groupId) {
  const t = (a.action_type || "recommended").toLowerCase();
  if (groupId === "remediation") return t === "recommended";
  if (groupId === "verification") return t === "check";
  if (groupId === "followup") return t === "followup";
  if (groupId === "followup_verification") return t === "followup_check";
  if (groupId === "other") {
    return t !== "recommended" && t !== "check" && t !== "followup" && t !== "followup_check";
  }
  return false;
}

/**
 * For each group: only top-level rows of that kind, each followed by its nested sub-steps
 * (and deeper trail chains) in one contiguous block.
 */
function bucketChecklistActions(actions) {
  if (!actions.length) {
    return [];
  }
  const { byId, byParent } = buildParentChildrenMap(actions);
  const order = rootOrderInActions(actions);

  const roots = actions.filter((a) => isRootNode(a));
  const orphanTrails = actions.filter(
    (a) => a.parent_action_id && !byId[a.parent_action_id],
  );

  const out = [];
  for (const g of CHECKLIST_GROUPS) {
    if (g.id === "substep") {
      if (orphanTrails.length) {
        out.push({
          ...g,
          items: orphanTrails.map((a) => ({ action: a, depth: 0 })),
        });
      }
      continue;
    }
    if (g.id === "other" && !roots.some((a) => rootMatchesGroup(a, "other"))) {
      continue;
    }
    if (g.id === "other") {
      const list = roots.filter((a) => rootMatchesGroup(a, "other"));
      if (list.length) {
        out.push({
          ...g,
          items: list
            .sort((a, b) => (order.get(a.id) ?? 0) - (order.get(b.id) ?? 0))
            .map((a) => ({ action: a, depth: 0 })),
        });
      }
      continue;
    }
    const groupRoots = roots
      .filter((a) => rootMatchesGroup(a, g.id))
      .sort((a, b) => (order.get(a.id) ?? 0) - (order.get(b.id) ?? 0));

    if (!groupRoots.length) {
      continue;
    }
    const items = [];
    for (const r of groupRoots) {
      items.push(...walkActionSubtrees(r, byParent));
    }
    out.push({ ...g, items });
  }
  return out;
}

function renderChecklistRows(items, byActionId) {
  return items.map(({ action: a, depth }) => {
    const kind = actionKind(a, byActionId);
    const isNested = depth > 0;
    const t = (a.action_type || "recommended").toLowerCase();
    const isEngFollowup = t === "followup" || t === "followup_check";
    const showBadges = isNested || isEngFollowup;
    const pad = isNested ? 12 + Math.min(depth, 4) * 16 : undefined;
    return (
      <tr
        key={a.id}
        className={isNested ? "audit-tr-nested" : undefined}
        data-depth={String(depth)}
      >
        <td
          className="audit-col-kind"
          style={pad != null ? { paddingLeft: pad } : undefined}
        >
          {showBadges ? (
            <div className="audit-badge-row">
              {isNested ? <AuditBadge variant="substep">Sub-step</AuditBadge> : null}
              {isEngFollowup ? (
                <AuditBadge variant="engineer-followup">Engineer follow-up</AuditBadge>
              ) : null}
            </div>
          ) : null}
          <span className="audit-type-title">{kind.title}</span>
          {kind.subtitle ? <span className="audit-type-sub">{kind.subtitle}</span> : null}
        </td>
        <td className="audit-col-status">{formatStatus(a.status)}</td>
        <td className="audit-col-sev">{formatSeverity(a.severity)}</td>
        <td style={pad != null ? { paddingLeft: pad } : undefined}>
          <div>{a.action_text}</div>
          <EngineerFollowupContext action={a} byId={byActionId} />
        </td>
        <td>
          {a.notes ? <div className="audit-note">{a.notes}</div> : null}
          {a.eval_response ? (
            <div className="audit-eval audit-eval-labeled" style={{ marginTop: a.notes ? 8 : 0 }}>
              <span className="audit-eval-label">Evaluation</span>
              {a.eval_response}
            </div>
          ) : null}
        </td>
      </tr>
    );
  });
}

function EngineerFollowupContext({ action, byId }) {
  const t = (action.action_type || "").toLowerCase();
  if (t !== "followup" && t !== "followup_check") return null;

  const anchor = action.source_anchor_action_id
    ? byId[action.source_anchor_action_id]
    : null;

  return (
    <div
      className="audit-eng-fu"
      style={{
        marginTop: 10,
        padding: "10px 12px",
        borderRadius: "var(--radius-sm)",
        background: "rgba(167, 139, 250, 0.08)",
        border: "1px solid rgba(167, 139, 250, 0.28)",
      }}
    >
      <p
        style={{
          margin: 0,
          fontSize: 10,
          fontWeight: 800,
          color: "var(--violet)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
        }}
      >
        Created from the engineer follow-up step
      </p>
      <p className="muted small" style={{ margin: "6px 0 0", lineHeight: 1.45 }}>
        These checklist lines were <strong>added</strong> after an engineer submitted additional findings
        (remediation follow-up). They are not part of the original plan.
      </p>
      {action.source_anchor_action_id ? (
        <p className="muted small" style={{ margin: "8px 0 0" }}>
          <span style={{ fontWeight: 600, color: "var(--text)" }}>Related to step: </span>
          {anchor?.action_text ? (
            <span title={action.source_anchor_action_id}>
              {truncate(anchor.action_text, 100)}
            </span>
          ) : (
            <code className="audit-mono small">{action.source_anchor_action_id}</code>
          )}
        </p>
      ) : null}
      {action.engineer_submission ? (
        <details className="audit-details" style={{ marginTop: 8 }}>
          <summary className="muted small" style={{ cursor: "pointer", userSelect: "none" }}>
            View engineer submission (the reported findings)
          </summary>
          <pre
            className="audit-pre"
            style={{ marginTop: 8, maxHeight: 200, fontSize: 12 }}
          >
            {action.engineer_submission}
          </pre>
        </details>
      ) : (
        <p className="muted small" style={{ margin: "8px 0 0" }}>
          The submission text is not on file for this run (data captured before this feature).
        </p>
      )}
    </div>
  );
}

export default function AuditTrailView({ workflow }) {
  if (!workflow) return null;

  const job = workflow.job || {};
  const pe = workflow.pipeline_events || [];
  const lastStage = pe.length ? pe[pe.length - 1].stage : job.current_stage;
  const timelineJob = {
    status: job.status,
    error: job.error,
    current_stage: lastStage,
  };
  const analysis = workflow.analysis || null;
  const sim = workflow.similar_incidents || [];
  const clar = workflow.clarification_answers;
  const clarQa = Array.isArray(workflow.clarification_qa) ? workflow.clarification_qa : null;
  const actions = workflow.remediation_actions || [];
  const chatByAction = workflow.remediation_chat || {};
  const pir = workflow.post_incident_review;
  const inc = workflow.incident;

  const chatActionIds = Object.keys(chatByAction);
  const byActionId = buildActionIndex(actions);

  return (
    <div className="audit-trail-root">
      <Section title="Run metadata" id="audit-meta">
        <KeyValueList
          items={[
            { k: "Job ID", v: <code className="audit-mono">{job.job_id}</code> },
            { k: "Incident ID", v: <code className="audit-mono">{job.incident_id}</code> },
            { k: "Status", v: formatStatus(job.status) },
            { k: "Current stage (last event)", v: formatPipelineStageId(lastStage) },
            { k: "Created", v: formatWhen(job.created_at) },
            { k: "Completed", v: formatWhen(job.completed_at) },
            { k: "Export snapshot", v: formatWhen(workflow.exported_at) },
          ]}
        />
        {job.error ? (
          <p className="error compact" style={{ marginTop: 12 }} role="alert">
            {job.error}
          </p>
        ) : null}
      </Section>

      <div style={{ marginBottom: 20 }}>
        <RunTimeline job={timelineJob} pipelineEvents={pe} running={false} />
      </div>

      {analysis ? (
        <>
          {analysis.summary ? (
            <Section title="Summary" id="audit-summary">
              <KeyValueList
                items={[
                  { k: "Severity", v: formatSeverity(analysis.summary.severity) },
                  { k: "Reason", v: <span className="audit-inline">{analysis.summary.severity_reason}</span> },
                ]}
              />
              <TextBlock text={analysis.summary.summary} />
            </Section>
          ) : null}

          {analysis.root_cause ? (
            <Section title="Root cause" id="audit-rca">
              <KeyValueList
                items={[
                  { k: "Confidence", v: formatSeverity(analysis.root_cause.confidence) },
                ]}
              />
              <TextBlock text={analysis.root_cause.likely_root_cause} />
              {analysis.root_cause.reasoning ? (
                <>
                  <p className="muted small" style={{ margin: "12px 0 4px" }}>
                    Reasoning
                  </p>
                  <TextBlock text={analysis.root_cause.reasoning} />
                </>
              ) : null}
            </Section>
          ) : null}

          {analysis.remediation ? (
            <Section title="Remediation plan (analysis)" id="audit-rem-plan">
              <p className="muted small" style={{ margin: "0 0 8px" }}>
                Risk if unresolved
              </p>
              <TextBlock text={analysis.remediation.risk_if_unresolved} />
              {(analysis.remediation.recommended_actions || []).length > 0 ? (
                <>
                  <p className="muted small" style={{ margin: "12px 0 6px" }}>
                    Recommended actions
                  </p>
                  <ol className="audit-numbered">
                    {analysis.remediation.recommended_actions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ol>
                </>
              ) : null}
              {(analysis.remediation.next_checks || []).length > 0 ? (
                <>
                  <p className="muted small" style={{ margin: "12px 0 6px" }}>
                    Next checks
                  </p>
                  <ol className="audit-numbered">
                    {analysis.remediation.next_checks.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ol>
                </>
              ) : null}
            </Section>
          ) : null}
        </>
      ) : (
        <Section title="Analysis">
          <p className="muted small">No analysis payload (job may have failed or still be running).</p>
        </Section>
      )}

      {clarQa && clarQa.length > 0 ? (
        <Section title="Clarification: questions and answers" id="audit-clarify">
          <p className="muted small" style={{ margin: "0 0 12px" }}>
            Questions asked to refine the plan before rebuilding remediation, and the operator answers
            (same as the Clarify step in the product).
          </p>
          <div className="audit-clar-qa">
            {clarQa.map((row) => (
              <div key={row.question_id} className="audit-clar-row">
                <div className="audit-clar-badges">
                  <AuditBadge variant="followup-question">Follow-up question</AuditBadge>
                </div>
                <p className="audit-clar-question">
                  {row.question ? (
                    row.question
                  ) : (
                    <span>
                      <span className="muted small">Question ID: </span>
                      <code className="audit-mono small">{row.question_id}</code>
                    </span>
                  )}
                </p>
                {row.kind ? (
                  <p className="audit-clar-kind muted small" style={{ margin: "2px 0 6px" }}>
                    Response type: {formatQuestionKind(row.kind)}
                  </p>
                ) : null}
                {row.rationale ? (
                  <p className="audit-clar-why muted small" style={{ margin: "0 0 8px" }}>
                    Why we ask: {row.rationale}
                  </p>
                ) : null}
                <p className="audit-clar-answerlabel muted small" style={{ margin: "0 0 4px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Answer</p>
                <p className="audit-clar-a">
                  {row.answer == null || row.answer === "" ? "—" : String(row.answer)}
                </p>
              </div>
            ))}
          </div>
        </Section>
      ) : clar && Object.keys(clar).length > 0 ? (
        <Section title="Clarification: questions and answers" id="audit-clarify-fallback">
          <p className="muted small" style={{ margin: "0 0 12px" }}>
            Operator responses (question text is unavailable without full analysis; open a fresh export after upgrade).
          </p>
          <div className="audit-clar-qa">
            {Object.entries(clar).map(([questionId, answer]) => (
              <div key={questionId} className="audit-clar-row">
                <div className="audit-clar-badges">
                  <AuditBadge variant="followup-question">Follow-up question</AuditBadge>
                </div>
                <p className="audit-clar-q muted small">Question ID: {questionId}</p>
                <p className="audit-clar-a">{answer == null || answer === "" ? "—" : String(answer)}</p>
              </div>
            ))}
          </div>
        </Section>
      ) : null}

      {sim.length > 0 ? (
        <Section title="Similar incidents" id="audit-similar">
          <ul className="audit-bullets">
            {sim.map((s, i) => (
              <li key={s.incident_id || i}>
                <code className="audit-mono">{s.incident_id || s.id}</code>
                {s.title ? <span> — {s.title}</span> : null}
                {s.similarity != null ? (
                  <span className="muted small" style={{ marginLeft: 6 }}>
                    score {s.similarity}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        </Section>
      ) : null}

      <Section title="Remediation and verification checklist" id="audit-actions">
        {actions.length === 0 ? (
          <p className="muted small">No checklist rows for this job.</p>
        ) : (
          <div className="audit-checklist-groups">
            {bucketChecklistActions(actions).map((group) => (
              <div key={group.id} className="audit-checklist-group">
                <h3 className="audit-checklist-group-title">{group.title}</h3>
                {group.blurb ? <p className="audit-checklist-group-blurb muted small">{group.blurb}</p> : null}
                <div className="audit-table-wrap">
                  <table className="audit-table audit-table-actions">
                    <thead>
                      <tr>
                        <th className="audit-col-kind">Kind</th>
                        <th className="audit-col-status">Status</th>
                        <th className="audit-col-sev">Severity</th>
                        <th>Action</th>
                        <th>Notes and evaluation</th>
                      </tr>
                    </thead>
                    <tbody>{renderChecklistRows(group.items, byActionId)}</tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      {chatActionIds.length > 0 ? (
        <Section title="Remediation chat" id="audit-chat">
          {chatActionIds.map((actionId) => (
            <div key={actionId || "none"} className="audit-chat-block" style={{ marginBottom: 16 }}>
              <p className="muted small" style={{ margin: "0 0 6px" }}>
                Action <code className="audit-mono">{actionId || "(none)"}</code>
              </p>
              <ul className="audit-chat-messages">
                {(chatByAction[actionId] || []).map((m) => (
                  <li key={m.id} className={m.role === "user" ? "is-user" : "is-asst"}>
                    <span className="audit-chat-role">{formatChatRole(m.role)}</span>
                    <span className="audit-chat-time muted small">{formatWhen(m.created_at)}</span>
                    <div className="audit-chat-body">{m.content}</div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </Section>
      ) : null}

      {pir ? (
        <Section title="Post-incident review" id="audit-pir">
          <TextBlock text={pir.timeline} />
          {pir.what_went_wrong ? (
            <>
              <p className="muted small" style={{ margin: "10px 0 4px" }}>
                What went wrong
              </p>
              <TextBlock text={pir.what_went_wrong} />
            </>
          ) : null}
          {pir.what_went_right ? (
            <>
              <p className="muted small" style={{ margin: "10px 0 4px" }}>
                What went right
              </p>
              <TextBlock text={pir.what_went_right} />
            </>
          ) : null}
          {(pir.action_summary || []).length > 0 ? (
            <>
              <p className="muted small" style={{ margin: "10px 0 4px" }}>
                Action summary
              </p>
              <ul className="audit-bullets">
                {pir.action_summary.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </>
          ) : null}
          {pir.lessons_learned ? (
            <>
              <p className="muted small" style={{ margin: "10px 0 4px" }}>
                Lessons learned
              </p>
              <TextBlock text={pir.lessons_learned} />
            </>
          ) : null}
        </Section>
      ) : null}

      {inc ? (
        <Section title="Incident record" id="audit-incident">
          <KeyValueList
            items={[
              { k: "Title", v: inc.title },
              { k: "Source", v: inc.source ? String(inc.source).replace(/\b\w/g, (c) => c.toUpperCase()) : "—" },
              { k: "Status", v: formatStatus(inc.status) },
              { k: "Assigned", v: inc.assigned_to || "—" },
              { k: "Resolved", v: formatWhen(inc.resolved_at) },
            ]}
          />
          {inc.resolution_notes ? (
            <>
              <p className="muted small" style={{ margin: "10px 0 4px" }}>
                Resolution notes
              </p>
              <TextBlock text={inc.resolution_notes} />
            </>
          ) : null}
          <details className="audit-details" style={{ marginTop: 12 }}>
            <summary className="muted small">Raw / sanitized log text</summary>
            {inc.sanitized_text != null && inc.sanitized_text !== "" ? (
              <pre className="audit-pre">{inc.sanitized_text}</pre>
            ) : null}
            {inc.raw_text != null && inc.raw_text !== inc.sanitized_text ? (
              <pre className="audit-pre">{inc.raw_text}</pre>
            ) : null}
          </details>
        </Section>
      ) : null}
    </div>
  );
}
