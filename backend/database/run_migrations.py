"""Initialize local Sentinel DB schema (SQLite for MVP local dev)."""

from __future__ import annotations

from src.db import get_database


def main() -> None:
    db = get_database()
    db.close()
    print("Migrations complete (SQLite schema ensured).")


if __name__ == "__main__":
    main()
