"""Tail CloudWatch logs for Sentinel agent functions."""

from __future__ import annotations

import argparse
import subprocess


LOG_GROUPS = [
    "/aws/lambda/sentinel-planner",
    "/aws/lambda/sentinel-normalizer",
    "/aws/lambda/sentinel-summarizer",
    "/aws/lambda/sentinel-investigator",
    "/aws/lambda/sentinel-remediator",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--since", default="30m")
    args = parser.parse_args()

    print("Tailing Sentinel agent logs (Ctrl+C to stop)")
    for group in LOG_GROUPS:
        print(f"\n=== {group} ===")
        subprocess.run(["aws", "logs", "tail", group, "--since", args.since, "--region", args.region], check=False)


if __name__ == "__main__":
    main()
