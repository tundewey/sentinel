"""Intel service local smoke test."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from intel.server import IntelRequest, intel


def main() -> None:
    response = intel(IntelRequest(text="ERROR timeout while calling payment service"))
    assert response["severity"] in {"high", "critical"}, response
    print("Intel test passed")


if __name__ == "__main__":
    main()
