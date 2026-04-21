import { RedirectToSignIn, SignedIn, SignedOut, UserButton, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { fetchCurrentUser, fetchIncidents, fetchJob } from "../lib/api";
import { isClerkEnabled } from "../lib/clerk";

const clerkEnabled = isClerkEnabled();

function DashboardContent({ tokenProvider = null, showIdentity = false }) {
  const [incidents, setIncidents] = useState([]);
  const [jobId, setJobId] = useState("");
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [me, setMe] = useState(null);

  async function loadIncidents() {
    try {
      const token = tokenProvider ? await tokenProvider() : null;
      const incidentData = await fetchIncidents(30, token);
      setIncidents(incidentData);
      if (showIdentity) {
        const meData = await fetchCurrentUser(token);
        setMe(meData);
      }
    } catch (err) {
      setError(err.message || "Failed to fetch incidents");
    }
  }

  useEffect(() => {
    loadIncidents();
  }, []);

  async function lookup(event) {
    event.preventDefault();
    setError("");
    setJob(null);
    try {
      const token = tokenProvider ? await tokenProvider() : null;
      const data = await fetchJob(jobId.trim(), token);
      setJob(data);
    } catch (err) {
      setError(err.message || "Failed to fetch job");
    }
  }

  return (
    <main className="container stack gap">
      <header className="hero card row between">
        <div>
          <h1>Sentinel Dashboard</h1>
          <p className="muted">Incident history and job lookup</p>
          {showIdentity && me ? <p className="muted">Signed in as: {me.user_id}</p> : null}
          {!clerkEnabled ? <p className="muted">Clerk disabled (configure real keys to enable SaaS auth).</p> : null}
        </div>
        <div className="row gap">
          <a href="/" className="btn btn-link">New Incident</a>
          {clerkEnabled ? <UserButton afterSignOutUrl="/" /> : null}
        </div>
      </header>

      <section className="card">
        <h2>Lookup Job</h2>
        <form className="row gap" onSubmit={lookup}>
          <input
            className="input"
            placeholder="Paste your job_id"
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
          />
          <button className="btn" type="submit" disabled={!jobId.trim()}>
            Fetch
          </button>
        </form>
        {job ? <pre className="code">{JSON.stringify(job, null, 2)}</pre> : <p className="muted">No job selected.</p>}
      </section>

      <section className="card">
        <h2>Your Recent Incidents</h2>
        {incidents.length === 0 ? <p className="muted">No incidents yet.</p> : null}
        <ul className="list">
          {incidents.map((item) => (
            <li key={item.incident_id}>
              <strong>{item.title || "Untitled incident"}</strong>
              <div className="muted">ID: {item.incident_id}</div>
              <div className="muted">Source: {item.source}</div>
              <div className="muted">Created: {item.created_at}</div>
            </li>
          ))}
        </ul>
      </section>

      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}

function AuthenticatedDashboard() {
  const { getToken } = useAuth();
  return <DashboardContent tokenProvider={getToken} showIdentity />;
}

export default function Dashboard() {
  if (!clerkEnabled) {
    return <DashboardContent />;
  }

  return (
    <>
      <SignedIn>
        <AuthenticatedDashboard />
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
