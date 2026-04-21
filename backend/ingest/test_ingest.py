"""Simple ingest lambda test."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from ingest.ingest_lambda import lambda_handler


def main() -> None:
    fd, path = tempfile.mkstemp(prefix="sentinel_ingest_test_", suffix=".db")
    os.close(fd)
    os.environ["SENTINEL_DB_PATH"] = path

    event = {
        "body": json.dumps(
            {
                "title": "Checkout outage",
                "source": "manual",
                "text": "ERROR: database connection refused during checkout",
            }
        )
    }
    result = lambda_handler(event, None)
    assert result["statusCode"] == 200, result
    print("Ingest test passed")


if __name__ == "__main__":
    main()
