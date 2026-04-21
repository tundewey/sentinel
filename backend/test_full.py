"""Extended local integration test for multiple incidents."""

from __future__ import annotations

import os
import tempfile

from common.models import IncidentInput
from common.pipeline import create_incident_and_job, run_job
from common.store import Database


SAMPLES = [
    IncidentInput(
        title="Auth failures",
        source="uploaded",
        text="ERROR 403 forbidden: access denied for service account",
    ),
    IncidentInput(
        title="Memory pressure",
        source="manual",
        text="WARN heap growth\nERROR OOM killed process in worker",
    ),
    IncidentInput(
        title="Unknown issue",
        source="manual",
        text="service seems unstable and users report intermittent issues",
    ),
]


def main() -> None:
    fd, path = tempfile.mkstemp(prefix="sentinel_backend_full_", suffix=".db")
    os.close(fd)
    os.environ["SENTINEL_DB_PATH"] = path

    db = Database(path)
    try:
        for sample in SAMPLES:
            _, job_id = create_incident_and_job(sample, db)
            result = run_job(job_id, db)
            assert result.status == "completed", result
            assert result.analysis is not None

        print("Backend full integration test passed (3/3 incidents)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
