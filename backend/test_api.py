"""API smoke test for Sentinel."""

from __future__ import annotations

import os
import tempfile

from fastapi.testclient import TestClient

from api.main import app


def main() -> None:
    fd, path = tempfile.mkstemp(prefix="sentinel_api_test_", suffix=".db")
    os.close(fd)
    os.environ["SENTINEL_DB_PATH"] = path
    os.environ["AUTH_DISABLED"] = "true"

    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200, health.text

    me = client.get("/api/me")
    assert me.status_code == 200, me.text
    assert me.json()["user_id"] == "dev_user"

    response = client.post(
        "/api/incidents/analyze-sync",
        json={
            "title": "Database instability",
            "source": "manual",
            "text": "ERROR database connection refused and timeout in checkout service",
        },
    )
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "completed", payload
    assert payload["analysis"]["summary"]["severity"] in {"high", "critical"}

    incidents = client.get("/api/incidents")
    assert incidents.status_code == 200, incidents.text
    assert len(incidents.json()) >= 1

    print("API smoke test passed")


if __name__ == "__main__":
    main()
