"""Bootstrap Sentinel local config files from examples."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        print(f"Skip existing: {dst}")
        return
    dst.write_text(src.read_text())
    print(f"Created: {dst}")


def main() -> None:
    copy_if_missing(ROOT / ".env.example", ROOT / ".env")

    for tf_dir in (ROOT / "terraform").iterdir():
        if tf_dir.is_dir() and (tf_dir / "terraform.tfvars.example").exists():
            copy_if_missing(tf_dir / "terraform.tfvars.example", tf_dir / "terraform.tfvars")

    copy_if_missing(ROOT / "frontend" / ".env.local.example", ROOT / "frontend" / ".env.local")


if __name__ == "__main__":
    main()
