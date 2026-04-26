import { useEffect, useMemo, useState } from "react";

function pretty(obj) {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

export default function ReplayPlayer({
  replay,
  onExplainFrame = null,
  explainResultByIndex = {},
  explainingIndex = null,
}) {
  const frames = replay?.frames || [];
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    setIndex(0);
    setPlaying(false);
  }, [replay?.job_id]);

  useEffect(() => {
    if (!playing || !frames.length) return;
    const t = setInterval(() => {
      setIndex((i) => {
        if (i >= frames.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, 1200);
    return () => clearInterval(t);
  }, [playing, frames.length]);

  const frame = useMemo(() => frames[index] || null, [frames, index]);

  if (!frames.length) {
    return <p className="muted small">No replay frames found for this run.</p>;
  }

  return (
    <section className="card-elevated" style={{ padding: "20px 24px" }}>
      <div className="row gap" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Replay</p>
          <h2 className="run-title" style={{ margin: 0 }}>
            {frame?.title || "Frame"} ({index + 1}/{frames.length})
          </h2>
          <p className="muted small" style={{ marginTop: 6 }}>
            {frame?.at ? new Date(frame.at).toLocaleString() : "No timestamp"}{frame?.detail ? ` · ${frame.detail}` : ""}
          </p>
        </div>
        <div className="row gap">
          <button className="btn btn-muted" type="button" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index <= 0}>
            Prev
          </button>
          <button className="btn" type="button" onClick={() => setPlaying((v) => !v)}>
            {playing ? "Pause" : "Play"}
          </button>
          <button className="btn btn-muted" type="button" onClick={() => setIndex((i) => Math.min(frames.length - 1, i + 1))} disabled={index >= frames.length - 1}>
            Next
          </button>
          {onExplainFrame ? (
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => onExplainFrame(index)}
              disabled={explainingIndex === index}
            >
              {explainingIndex === index ? "Explaining..." : "Explain Step"}
            </button>
          ) : null}
        </div>
      </div>

      <div style={{ marginTop: 14 }}>
        <input
          type="range"
          min={0}
          max={Math.max(0, frames.length - 1)}
          value={index}
          onChange={(e) => setIndex(Number(e.target.value))}
          style={{ width: "100%" }}
        />
      </div>

      <div className="grid two-col" style={{ marginTop: 16, gap: 12 }}>
        <div className="card" style={{ padding: 12 }}>
          <p className="muted small" style={{ margin: "0 0 8px" }}>Snapshot</p>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{pretty(frame?.snapshot || {})}</pre>
        </div>
        <div className="card" style={{ padding: 12 }}>
          <p className="muted small" style={{ margin: "0 0 8px" }}>Delta from previous step</p>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{pretty(frame?.delta || {})}</pre>
        </div>
      </div>

      {explainResultByIndex[index] ? (
        <div className="card" style={{ marginTop: 12, padding: 12 }}>
          <p style={{ margin: "0 0 8px" }}>
            <strong>AI Explain</strong> ·{" "}
            <span className="muted small">Confidence: {explainResultByIndex[index].confidence}</span>
          </p>
          <p style={{ margin: "0 0 8px" }}>{explainResultByIndex[index].explanation}</p>
          {(explainResultByIndex[index].evidence || []).length ? (
            <ul style={{ margin: 0 }}>
              {explainResultByIndex[index].evidence.map((ev, i) => (
                <li key={i}>{ev}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}