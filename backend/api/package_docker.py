"""Build API deployment package for Lambda."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    zip_path = ROOT / "api_lambda.zip"
    if zip_path.exists():
        zip_path.unlink()

    # Minimal placeholder zip build for local workflow.
    shutil.make_archive(str(ROOT / "api_lambda"), "zip", root_dir=ROOT)
    print(f"Created {zip_path.name}")


if __name__ == "__main__":
    main()
