const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const token = options.token;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  return res.json();
}

export async function analyzeIncident(payload, token) {
  return request("/api/incidents/analyze-sync", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export async function fetchIncidents(limit = 25, token) {
  return request(`/api/incidents?limit=${limit}`, { token });
}

export async function fetchJob(jobId, token) {
  return request(`/api/jobs/${jobId}`, { token });
}

export async function fetchCurrentUser(token) {
  return request("/api/me", { token });
}
