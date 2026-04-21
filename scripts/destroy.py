"""Destroy Sentinel Terraform stacks in reverse order."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORDER = [
    "8_enterprise",
    "7_frontend",
    "6_agents",
    "5_database",
    "4_intel",
    "3_ingestion",
    "2_sagemaker",
]


def main() -> None:
    for stage in ORDER:
        tf_dir = ROOT / "terraform" / stage
        print(f"Destroying {stage}...")
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=tf_dir, check=False)


if __name__ == "__main__":
    main()
