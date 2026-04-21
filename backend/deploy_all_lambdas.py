"""Deploy packaged Sentinel Lambda artifacts to AWS."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def deploy(function_name: str, zip_path: Path, region: str) -> None:
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing package: {zip_path}")

    subprocess.run(
        [
            "aws",
            "lambda",
            "update-function-code",
            "--function-name",
            function_name,
            "--zip-file",
            f"fileb://{zip_path}",
            "--region",
            region,
        ],
        check=True,
    )
    print(f"Updated {function_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--include-api", action="store_true")
    parser.add_argument("--include-ingest", action="store_true")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()

    if args.package:
        subprocess.run(
            [
                "uv",
                "run",
                "package_docker.py",
                *(["--include-api"] if args.include_api else []),
                *(["--include-ingest"] if args.include_ingest else []),
            ],
            cwd=ROOT,
            check=True,
        )

    mapping = {
        "sentinel-planner": ROOT / "planner" / "planner_lambda.zip",
        "sentinel-normalizer": ROOT / "normalizer" / "normalizer_lambda.zip",
        "sentinel-summarizer": ROOT / "summarizer" / "summarizer_lambda.zip",
        "sentinel-investigator": ROOT / "investigator" / "investigator_lambda.zip",
        "sentinel-remediator": ROOT / "remediator" / "remediator_lambda.zip",
    }

    if args.include_api:
        mapping["sentinel-api"] = ROOT / "api" / "api_lambda.zip"

    if args.include_ingest:
        mapping["sentinel-ingest"] = ROOT / "ingest" / "ingest_lambda.zip"

    for fn_name, artifact in mapping.items():
        deploy(fn_name, artifact, args.region)


if __name__ == "__main__":
    main()
