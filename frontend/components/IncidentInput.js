import { useRef, useState } from "react";

export default function IncidentInput({ onAnalyze, loading }) {
  const [title, setTitle] = useState("Production incident");
  const [source, setSource] = useState("manual");
  const [text, setText] = useState("");
  const fileRef = useRef(null);

  async function onFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const value = await file.text();
    setText(value);
    setSource("upload");
  }

  function submit(event) {
    event.preventDefault();
    onAnalyze({ title: title.trim(), source, text: text.trim() });
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <h2>Incident Input</h2>
      <label>
        Incident Title
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
        />
      </label>
      <label>
        Incident Source
        <select className="input" value={source} onChange={(e) => setSource(e.target.value)}>
          <option value="manual">Manual paste</option>
          <option value="upload">File upload</option>
          <option value="monitoring">Monitoring export</option>
        </select>
      </label>
      <label>
        Paste Logs / Incident Text
        <textarea
          className="input textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste logs, stack trace, and context here..."
          required
        />
      </label>
      <div className="row gap">
        <button type="button" className="btn btn-muted" onClick={() => fileRef.current?.click()}>
          Upload Log File
        </button>
        <input ref={fileRef} type="file" accept=".txt,.log,.md,.json" hidden onChange={onFileChange} />
        <button type="submit" className="btn" disabled={loading || !text.trim()}>
          {loading ? "Analyzing..." : "Analyze Incident"}
        </button>
      </div>
    </form>
  );
}
