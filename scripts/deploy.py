"""Deploy helper for frontend static assets and optional CloudFront invalidation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    run(["npm", "run", "build"], cwd=FRONTEND)

    bucket = os.getenv("SENTINEL_FRONTEND_BUCKET", "")
    dist_id = os.getenv("SENTINEL_CLOUDFRONT_DISTRIBUTION_ID", "")
    if not bucket:
        print("Build complete. Set SENTINEL_FRONTEND_BUCKET to enable S3 upload.")
        return

    run(["aws", "s3", "sync", str(FRONTEND / "out"), f"s3://{bucket}", "--delete"])
    print(f"Uploaded frontend to s3://{bucket}")

    if dist_id:
        run(["aws", "cloudfront", "create-invalidation", "--distribution-id", dist_id, "--paths", "/*"])
        print(f"Invalidated CloudFront distribution {dist_id}")


if __name__ == "__main__":
    main()
