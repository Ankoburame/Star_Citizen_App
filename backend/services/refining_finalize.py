from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.refining import RefiningJob


def finalize_ready_refining_jobs(db: Session) -> int:
    """
    Finalise les raffinages terminés (PostgreSQL safe).
    """

    now = datetime.utcnow()

    jobs = (
        db.query(RefiningJob)
        .filter(
            RefiningJob.status == "RUNNING",
            text(
                "refining_jobs.started_at + "
                "(refining_jobs.duration_minutes || ' minutes')::interval <= :now"
            ),
        )
        .params(now=now)
        .all()
    )

    count = 0

    for job in jobs:
        job.status = "DONE"
        job.completed_at = now
        count += 1

    if count:
        db.commit()

    return count
