from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models.refining import RefiningJob
from services.refining_service import start_refining
from services.refining_finalize import finalize_ready_refining_jobs
from services.dashboard_service import broadcast_dashboard


router = APIRouter()


# =========================
# SCHEMA (LOCAL, EXPLICITE)
# =========================
class RefiningCreate(BaseModel):
    input_material_id: int
    output_material_id: int
    input_quantity: int
    output_quantity: int
    duration_minutes: int


# =========================
# ACTIVE JOBS
# =========================
@router.get("/active")
def get_active_refining(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    completed_jobs = finalize_ready_refining_jobs(db)

    if completed_jobs > 0:
        background_tasks.add_task(broadcast_dashboard, db)

    now = datetime.utcnow()

    jobs = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .all()
    )

    return [
        {
            "id": job.id,
            "material_name": job.output_material.name if job.output_material else "Unknown",
            "quantity": job.output_quantity,
            "remaining_seconds": max(
                0,
                int(
                    (job.started_at + timedelta(minutes=job.duration_minutes) - now
                ).total_seconds())
            ),
            "total_seconds": job.duration_minutes * 60,
        }
        for job in jobs
    ]


# =========================
# HISTORY
# =========================
@router.get("/history")
def get_refining_history(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    jobs = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "DONE")
        .order_by(RefiningJob.completed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": job.id,
            "material": job.output_material.name if job.output_material else "Unknown",
            "quantity": job.output_quantity,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "duration_minutes": job.duration_minutes,
        }
        for job in jobs
    ]


# =========================
# START REFINING
# =========================
@router.post("/start")
def start_refining_job(
    data: RefiningCreate,
    db: Session = Depends(get_db),
):
    job_id = start_refining(
        input_material_id=data.input_material_id,
        output_material_id=data.output_material_id,
        input_quantity=data.input_quantity,
        output_quantity=data.output_quantity,
        duration_minutes=data.duration_minutes,
        db=db,
    )

    return {"job_id": job_id}
