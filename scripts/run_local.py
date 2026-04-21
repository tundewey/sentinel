"""Run Sentinel backend API and frontend dev servers together."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def main() -> None:
    backend_cmd = ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
    frontend_cmd = ["npm", "run", "dev"]

    backend_env = os.environ.copy()
    if not backend_env.get("CLERK_JWKS_URL") and not backend_env.get("CLERK_ISSUER"):
        backend_env.setdefault("AUTH_DISABLED", "true")

    backend = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR, env=backend_env)
    frontend = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

    print("Sentinel local dev started:")
    print("- Backend: http://localhost:8000")
    print("- Frontend: http://localhost:3000")
    if backend_env.get("AUTH_DISABLED") == "true":
        print("- Auth mode: AUTH_DISABLED=true (set Clerk env vars to enable auth)")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("Stopping services...")
    finally:
        for proc in (backend, frontend):
            if proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    main()
