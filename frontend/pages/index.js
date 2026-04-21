import { RedirectToSignIn, SignedIn, SignedOut, UserButton, useAuth } from "@clerk/nextjs";
import { useState } from "react";

import AnalysisCards from "../components/AnalysisCards";
import IncidentInput from "../components/IncidentInput";
import { analyzeIncident } from "../lib/api";
import { isClerkEnabled } from "../lib/clerk";

const clerkEnabled = isClerkEnabled();

function UnauthenticatedHome() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function onAnalyze(payload) {
    setLoading(true);
    setError("");
    try {
      const data = await analyzeIncident(payload, null);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to analyze incident");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container stack gap">
      <header className="hero card row between">
        <div>
          <h1>Odyssey Sentinel</h1>
          <p>AI-Powered Observability and Incident Intelligence Platform</p>
          <p className="muted">Clerk is disabled until real keys are configured.</p>
        </div>
        <a href="/dashboard" className="btn btn-link">Dashboard</a>
      </header>

      <IncidentInput onAnalyze={onAnalyze} loading={loading} />
      {error ? <p className="error">{error}</p> : null}
      <AnalysisCards result={result} />
    </main>
  );
}

function AuthenticatedHome() {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function onAnalyze(payload) {
    setLoading(true);
    setError("");
    try {
      const token = await getToken();
      const data = await analyzeIncident(payload, token);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to analyze incident");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container stack gap">
      <header className="hero card row between">
        <div>
          <h1>Odyssey Sentinel</h1>
          <p>AI-Powered Observability and Incident Intelligence Platform</p>
        </div>
        <div className="row gap">
          <a href="/dashboard" className="btn btn-link">Dashboard</a>
          <UserButton afterSignOutUrl="/" />
        </div>
      </header>

      <IncidentInput onAnalyze={onAnalyze} loading={loading} />
      {error ? <p className="error">{error}</p> : null}
      <AnalysisCards result={result} />
    </main>
  );
}

export default function Home() {
  if (!clerkEnabled) {
    return <UnauthenticatedHome />;
  }

  return (
    <>
      <SignedIn>
        <AuthenticatedHome />
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
