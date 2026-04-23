"""Management-grade PDF: cover sheet, document control, executive summary, sectioned body, page numbers."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from fpdf import FPDF

from common.pdf_report import _check_page_break, _epw, _multi_cell, _safe

# Navy + neutrals; suitable for print and screen
_NAVY = (18, 42, 86)
_SLATE = (64, 72, 88)
_MUTED = (102, 108, 120)


def _ts(iso: str | None) -> str:
    if not iso:
        return "—"
    s = str(iso).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:  # noqa: BLE001
        return s[:19]


def _one_line(s: str | None, n: int = 500) -> str:
    t = re.sub(r"\s+", " ", (s or "")).strip()
    if len(t) > n:
        return t[: n - 1] + "…"
    return t or "—"


class _ManagementAuditPDF(FPDF):
    """Page 1 = cover (no running header). From page 2: title strip + page x / n."""

    def __init__(self, short_ref: str) -> None:
        super().__init__(format="A4", unit="mm")
        self.short_ref = short_ref
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(18, 20, 18)
        self.alias_nb_pages()
        self._in_body = False

    def set_body_started(self) -> None:
        self._in_body = True

    def header(self) -> None:
        if not self._in_body or self.page_no() < 2:
            return
        self.set_y(12)
        self.set_text_color(*_NAVY)
        self.set_font("Helvetica", "B", 8.5)
        self.cell(0, 4, "Incident workflow and audit record", align="L", ln=True)
        self.set_y(12)
        self.set_text_color(*_MUTED)
        self.set_font("Helvetica", "", 7.5)
        self.cell(0, 4, f"Ref. {self.short_ref}  (internal)", align="R", ln=True)
        self.set_draw_color(210, 214, 222)
        self.set_line_width(0.25)
        y = float(self.get_y()) + 0.5
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        self.set_y(-11)
        self.set_text_color(*_MUTED)
        self.set_font("Helvetica", "I", 7)
        w = _epw(self) / 2
        self.cell(w, 3, "Sentinel  ·  Confidential  ·  Management and audit use", align="L")
        self.set_font("Helvetica", "", 7)
        self.cell(w, 3, f"Page {self.page_no()}/{{nb}}", align="R", ln=True)
        self.set_text_color(0, 0, 0)


def _order_actions_for_audit(actions: list[dict[str, Any]]) -> list[tuple[dict[str, Any], int]]:
    if not actions:
        return []
    by_parent: dict[str | None, list[dict[str, Any]]] = {}
    for a in actions:
        pid = a.get("parent_action_id") or None
        if pid not in by_parent:
            by_parent[pid] = []
        by_parent[pid].append(a)
    for lst in by_parent.values():
        lst.sort(key=lambda x: (x.get("created_at") or ""))
    out: list[tuple[dict[str, Any], int]] = []
    seen: set[str] = set()

    def visit(node: dict[str, Any], depth: int) -> None:
        out.append((node, depth))
        seen.add(node.get("id", ""))
        for ch in by_parent.get(node.get("id"), []):
            visit(ch, depth + 1)

    roots = [a for a in actions if not a.get("parent_action_id")]
    roots.sort(key=lambda x: (x.get("created_at") or ""))
    for r in roots:
        visit(r, 0)
    for a in actions:
        if a.get("id") not in seen and a.get("id"):
            out.append((a, 0))
    return out


def _kind_line(action: dict[str, Any]) -> str:
    t = (action.get("action_type") or "recommended").lower()
    if action.get("parent_action_id"):
        return "Sub-step"
    if t == "recommended":
        return "Remediation"
    if t == "check":
        return "Verification"
    if t == "followup":
        return "Follow-up action"
    if t == "followup_check":
        return "Follow-up check"
    return t


def _draw_cover_header(pdf: FPDF) -> None:
    pdf.set_fill_color(*_NAVY)
    pdf.rect(0, 0, pdf.w, 30, "F")
    pdf.set_y(7)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_x(0)
    pdf.cell(pdf.w, 7, "INCIDENT WORKFLOW AND AUDIT RECORD", align="C", ln=True)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(200, 210, 230)
    pdf.set_x(0)
    pdf.cell(
        pdf.w, 4, "Sentinel  ·  Odyssey  ·  Complete, read-only record for leadership and compliance",
        align="C",
        ln=True,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(34)


def _draw_kv_table(pdf: FPDF, title: str, rows: list[tuple[str, str]]) -> None:
    if title:
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*_NAVY)
        pdf.cell(_epw(pdf), 5, _safe(title), ln=True)
        pdf.ln(0.5)
    w_lab = 56.0
    w_val = _epw(pdf) - w_lab
    pdf.set_text_color(0, 0, 0)
    for lab, val in rows:
        _check_page_break(pdf, 12)
        y0 = float(pdf.get_y())
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_SLATE)
        pdf.set_xy(pdf.l_margin, y0)
        pdf.cell(w_lab, 5, _safe(lab)[:32], border="LRT", align="L")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(20, 22, 28)
        pdf.set_xy(pdf.l_margin + w_lab, y0)
        vs = _safe(str(val) if val is not None else "—")[:12000]
        pdf.multi_cell(w_val, 4, vs, border="LRT", align="L")
        h = max(5.0, pdf.get_y() - y0)
        yb = y0 + h
        pdf.set_draw_color(200, 204, 214)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, yb, pdf.l_margin + w_lab + w_val, yb)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)


def _section(pdf: FPDF, num: int, title: str, blurb: str | None = None) -> None:
    _check_page_break(pdf, 20)
    pdf.ln(2.5)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*_NAVY)
    pdf.set_x(pdf.l_margin)
    pdf.cell(_epw(pdf), 6, _safe(f"Section {num}  —  {title}"), ln=True)
    if blurb:
        pdf.ln(0.5)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*_MUTED)
        _multi_cell(pdf, blurb, 3.8)
        pdf.ln(0.3)
    pdf.set_draw_color(190, 196, 208)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y() + 0.3, pdf.l_margin + _epw(pdf), pdf.get_y() + 0.3)
    pdf.ln(3.5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9.5)


def _action_blocks(
    pdf: FPDF, ordered: list[tuple[dict[str, Any], int]]
) -> None:
    if not ordered:
        _multi_cell(pdf, "No checklist items for this run.", 4.2)
        return
    for idx, (action, depth) in enumerate(ordered):
        _check_page_break(pdf, 24)
        kind = _kind_line(action)
        if depth:
            kind = "    " * min(depth, 4) + kind
        status = str(action.get("status", "—"))
        sev = str(action.get("severity", "—"))
        line = f"{kind}   —   {status}   —   {sev}"
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(*_NAVY)
        _multi_cell(pdf, line[:180], 3.8)
        pdf.set_font("Helvetica", "", 9.0)
        pdf.set_text_color(25, 25, 32)
        _multi_cell(pdf, str(action.get("action_text", "") or "—")[:10000], 4.0)
        extra: list[str] = []
        if action.get("notes"):
            extra.append(f"Engineer notes: {action.get('notes', '')[:1500]}")
        if action.get("eval_response"):
            extra.append(f"Evaluation: {action.get('eval_response', '')[:1500]}")
        if action.get("engineer_submission") and str(
            action.get("action_type", "")
        ).lower() in ("followup", "followup_check"):
            n = len(str(action.get("engineer_submission", "")))
            extra.append(f"Engineer submission on file ({n} characters).")
        if extra:
            pdf.ln(0.3)
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(*_MUTED)
            _multi_cell(pdf, "\n\n".join(extra)[:5000], 3.2)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1.5)
        if idx < len(ordered) - 1:
            pdf.set_draw_color(225, 228, 234)
            pdf.set_line_width(0.2)
            y = float(pdf.get_y())
            pdf.line(pdf.l_margin, y, pdf.l_margin + _epw(pdf), y)
        pdf.ln(1.2)


def render_audit_classic_pdf(workflow: dict[str, Any]) -> bytes:
    """
    Professional management PDF: cover + document control, executive framing, numbered sections,
    Helvetica, footer page count, light borders on metadata tables.
    """
    job = workflow.get("job") or {}
    job_id = str(job.get("job_id", "") or "")
    short = (job_id[:8] if len(job_id) >= 8 else job_id) or "--------"
    ref = f"SEN-AUD-{short.upper()}"

    pdf = _ManagementAuditPDF(ref)
    now = workflow.get("exported_at") or datetime.now(timezone.utc).isoformat()
    ver = workflow.get("export_version", 2)

    pdf.add_page()
    _draw_cover_header(pdf)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*_SLATE)
    _multi_cell(
        pdf,
        "This document records a read-only, point-in-time view of the incident analysis workflow, "
        "clarification responses, remediation checklist, and supporting materials. It is produced "
        "for management oversight, internal audit, and post-incident review.",
        4.2,
    )
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)

    _draw_kv_table(
        pdf,
        "Document control",
        [
            ("Reference", ref),
            ("Export format version", str(ver)),
            ("Generated (UTC)", _ts(now)),
            ("Job ID", str(job.get("job_id", "—"))),
            ("Incident ID", str(job.get("incident_id", "—"))),
            ("Run status", str(job.get("status", "—"))),
        ],
    )

    inc0 = workflow.get("incident") or {}
    if isinstance(inc0, dict) and (inc0.get("title") or inc0.get("id")):
        _draw_kv_table(
            pdf,
            "Incident (summary)",
            [
                ("Title", str(inc0.get("title", "—"))),
                ("Source", str(inc0.get("source", "—"))),
                ("Record status", str(inc0.get("status", "—"))),
            ],
        )

    an0 = workflow.get("analysis") or {}
    sm0 = (an0.get("summary") or {}) if isinstance(an0, dict) else {}
    _draw_kv_table(
        pdf,
        "Executive summary",
        [
            (
                "Severity (from analysis)",
                str(sm0.get("severity", "—") or "—").upper()
                if sm0.get("severity")
                else "—",
            ),
            ("Narrative overview", _one_line(sm0.get("summary", ""), 2000)),
        ],
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*_MUTED)
    pdf.cell(
        _epw(pdf), 4, "Detailed sections follow on the next page.", align="C", ln=True
    )
    pdf.set_text_color(0, 0, 0)

    # Body pages: running header, footers, sections
    pdf.set_body_started()
    pdf.add_page()
    n = 0

    def next_section() -> int:
        nonlocal n
        n += 1
        return n

    s = next_section()
    _section(
        pdf,
        s,
        "Run and pipeline",
        "Timestamps and automated pipeline stages for this job.",
    )
    j = job
    _draw_kv_table(
        pdf,
        "",
        [
            ("Created (UTC)", _ts(j.get("created_at"))),
            ("Completed (UTC)", _ts(j.get("completed_at"))),
            ("Current stage (last event)", str(j.get("current_stage", "—"))),
            (
                "Error (if any)",
                str(j.get("error", "—") or "—")
                if j.get("error")
                else "None (no pipeline error on record).",
            ),
        ],
    )
    pe = workflow.get("pipeline_events") or []
    if pe:
        pdf.ln(0.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_NAVY)
        pdf.cell(_epw(pdf), 4, "Stage log (chronological)", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 8.2)
        for ev in pe[:120]:
            at = _ts(ev.get("at")) if ev.get("at") else "—"
            stg = str(ev.get("stage", ""))
            det = str(ev.get("detail", ""))[:200]
            _multi_cell(pdf, f"  {at}  |  {stg}  |  {det}", 3.5)

    s = next_section()
    _section(
        pdf,
        s,
        "Findings: summary and root cause",
        "Synthesized analysis suitable for readout; the platform retains full structured data.",
    )
    an = workflow.get("analysis") or {}
    sm = (an.get("summary") or {}) if isinstance(an, dict) else {}
    if sm:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_NAVY)
        pdf.cell(_epw(pdf), 4, "Impact and summary", ln=True)
        pdf.set_font("Helvetica", "", 9.2)
        pdf.set_text_color(30, 32, 40)
        _multi_cell(pdf, str(sm.get("summary", "—") or "—")[:20000], 4.0)
        if sm.get("severity_reason"):
            pdf.ln(0.5)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(*_SLATE)
            _multi_cell(
                pdf,
                f"Severity rationale: {sm.get('severity_reason', '')}"[:2000],
                3.8,
            )
        pdf.set_text_color(0, 0, 0)
    rc = (an.get("root_cause") or {}) if isinstance(an, dict) else {}
    if rc:
        pdf.ln(0.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_NAVY)
        pdf.cell(_epw(pdf), 4, "Likely root cause", ln=True)
        pdf.set_font("Helvetica", "", 9.2)
        _multi_cell(pdf, str(rc.get("likely_root_cause", "—") or "—")[:20000], 4.0)
        if rc.get("confidence") or rc.get("reasoning"):
            pdf.ln(0.3)
            pdf.set_font("Helvetica", "", 8.5)
            t = f"Confidence: {rc.get('confidence', '—')}"
            if rc.get("reasoning"):
                t += f"\n\nRationale: {rc.get('reasoning', '')}"
            _multi_cell(pdf, t[:20000], 3.8)

    cqa = workflow.get("clarification_qa")
    if cqa and isinstance(cqa, list) and len(cqa) > 0:
        s = next_section()
        _section(
            pdf,
            s,
            "Clarification responses",
            "Questions posed to improve remediation specificity; operator answers on record.",
        )
        for i, row in enumerate(cqa, 1):
            _check_page_break(pdf, 20)
            q = row.get("question") or f"Question ID: {row.get('question_id', '')}"
            a = str(row.get("answer", "—") or "—")
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*_NAVY)
            pdf.cell(_epw(pdf), 4, f"Item {i}", ln=True)
            pdf.set_font("Helvetica", "B", 8.2)
            pdf.set_text_color(30, 32, 40)
            _multi_cell(pdf, str(q)[:8000], 3.8)
            pdf.ln(0.3)
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_text_color(*_MUTED)
            pdf.cell(18, 3.3, "Response:", ln=False)
            pdf.set_font("Helvetica", "", 8.8)
            pdf.set_text_color(0, 0, 0)
            _multi_cell(pdf, a[:20000], 3.5)
            pdf.ln(1.2)

    s = next_section()
    _section(
        pdf,
        s,
        "Remediation and verification checklist",
        "Items are ordered; indented blocks are sub-steps under a parent. Status reflects operator progress.",
    )
    _action_blocks(
        pdf, _order_actions_for_audit(workflow.get("remediation_actions") or [])
    )

    chat = workflow.get("remediation_chat") or {}
    if isinstance(chat, dict) and chat:
        s = next_section()
        _section(
            pdf,
            s,
            "Assisted chat (excerpt)",
            "Optional AI-assisted thread per checklist line; excerpted for audit trail completeness.",
        )
        for aid, msgs in list(chat.items())[:40]:
            if not isinstance(msgs, list):
                continue
            _check_page_break(pdf, 10)
            pdf.set_font("Helvetica", "B", 8.2)
            pdf.set_text_color(*_NAVY)
            pdf.cell(
                _epw(pdf), 3.5, _safe(f"Action {str(aid)[:40] or '—'}"), ln=True
            )
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 8.0)
            for m in msgs[:40]:
                role = str(m.get("role", "")).capitalize()
                c = str(m.get("content", ""))[:2000]
                _multi_cell(pdf, f"  [{role}]  {c}", 3.2)
        pdf.ln(0.5)

    pir = workflow.get("post_incident_review")
    if isinstance(pir, dict) and pir:
        has_any = any(
            pir.get(k)
            for k in (
                "timeline",
                "what_went_wrong",
                "what_went_right",
                "lessons_learned",
                "action_summary",
                "prevention_steps",
            )
        )
        if has_any:
            s = next_section()
            _section(
                pdf,
                s,
                "Post-incident review",
                "Structured follow-up, when generated in the product.",
            )
            for key, label in (
                ("timeline", "Timeline"),
                ("what_went_wrong", "What went wrong"),
                ("what_went_right", "What went right"),
                ("lessons_learned", "Lessons learned"),
            ):
                if pir.get(key):
                    pdf.set_font("Helvetica", "B", 8.5)
                    pdf.set_text_color(*_NAVY)
                    pdf.cell(_epw(pdf), 4, label, ln=True)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Helvetica", "", 8.5)
                    _multi_cell(pdf, str(pir.get(key, "")), 3.6)
            summ = pir.get("action_summary") or []
            if isinstance(summ, list) and summ:
                pdf.ln(0.3)
                pdf.set_font("Helvetica", "B", 8.5)
                pdf.set_text_color(*_NAVY)
                pdf.cell(_epw(pdf), 4, "Action summary", ln=True)
                pdf.set_text_color(0, 0, 0)
                for i, t in enumerate(summ[:40], 1):
                    _multi_cell(pdf, f"  {i}.  {t}", 3.4)
            ps = pir.get("prevention_steps") or []
            if isinstance(ps, list) and ps:
                pdf.ln(0.3)
                pdf.set_font("Helvetica", "B", 8.5)
                pdf.set_text_color(*_NAVY)
                pdf.cell(_epw(pdf), 4, "Prevention steps", ln=True)
                pdf.set_text_color(0, 0, 0)
                for i, t in enumerate(ps[:40], 1):
                    _multi_cell(pdf, f"  {i}.  {t}", 3.4)

    inc = workflow.get("incident")
    if isinstance(inc, dict) and (inc.get("id") or inc.get("title")):
        s = next_section()
        _section(
            pdf,
            s,
            "Incident record (snapshot)",
        )
        _draw_kv_table(
            pdf,
            "",
            [
                ("Record ID", str(inc.get("id", "—"))),
                ("Title", str(inc.get("title", "—"))),
                ("Source", str(inc.get("source", "—"))),
                ("Status", str(inc.get("status", "—"))),
                (
                    "Resolved (UTC)",
                    _ts(inc.get("resolved_at")) if inc.get("resolved_at") else "— / open",
                ),
            ],
        )
        if inc.get("resolution_notes"):
            pdf.ln(0.5)
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*_NAVY)
            pdf.cell(_epw(pdf), 4, "Resolution notes", ln=True)
            pdf.set_text_color(0, 0, 0)
            _multi_cell(pdf, str(inc.get("resolution_notes", "")), 3.6)

    return bytes(pdf.output())
