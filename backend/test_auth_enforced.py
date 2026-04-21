"""Verify auth enforcement when AUTH_DISABLED=false."""

from __future__ import annotations

import os
import tempfile

from fastapi.testclient import TestClient

from api.main import app


def main() -> None:
    fd, path = tempfile.mkstemp(prefix="sentinel_auth_enforced_", suffix=".db")
    os.close(fd)
    os.environ["SENTINEL_DB_PATH"] = path
    os.environ["AUTH_DISABLED"] = "false"
    os.environ.pop("CLERK_JWKS_URL", None)
    os.environ.pop("CLERK_ISSUER", None)

    client = TestClient(app)
    response = client.get("/api/incidents")
    assert response.status_code == 401, response.text
    print("Auth enforcement test passed (missing token rejected).")


if __name__ == "__main__":
    main()
