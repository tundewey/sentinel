"""Build ingest deployment package."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    zip_base = ROOT / "ingest_lambda"
    zip_file = ROOT / "ingest_lambda.zip"
    if zip_file.exists():
        zip_file.unlink()
    shutil.make_archive(str(zip_base), "zip", root_dir=ROOT)
    print(f"Created {zip_file.name}")


if __name__ == "__main__":
    main()
