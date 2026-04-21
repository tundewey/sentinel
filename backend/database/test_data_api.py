"""Connectivity smoke test for Sentinel DB layer."""

from __future__ import annotations

from src.db import get_database


def main() -> None:
    db = get_database()
    incidents = db.list_incidents(limit=1)
    db.close()
    print("Database connectivity OK.")
    print(f"Existing incidents (up to 1 shown): {len(incidents)}")


if __name__ == "__main__":
    main()
