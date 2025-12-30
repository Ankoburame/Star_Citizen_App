"""
Refining API endpoints for Star Citizen App.
Manages refining jobs including starting, tracking active jobs, and viewing history.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models.refining import RefiningJob
from services.dashboard_service import broadcast_dashboard
from services.refining_finalize import finalize_ready_refining_jobs
from services.refining_service import start_refining

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class RefiningCreate(BaseModel):
    """Schema for creating a new refining job."""
    
    input_material_id: int = Field(..., gt=0, description="ID of the input material")
    output_material_id: int = Field(..., gt=0, description="ID of the output material")
    input_quantity: int = Field(..., gt=0, description="Quantity of input material")
    output_quantity: int = Field(..., gt=0, description="Quantity of output material")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")


class RefiningJobResponse(BaseModel):
    """Response schema for a single refining job."""
    
    job_id: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_refining(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Retrieve all active (running) refining jobs with their progress.
    
    This endpoint also finalizes any jobs that are ready and broadcasts
    dashboard updates if jobs were completed.
    
    Args:
        background_tasks: FastAPI background tasks manager
        db: Database session dependency
        
    Returns:
        List of active refining jobs with material name, quantity, 
        and remaining/total seconds
    """
    # Finalize any completed jobs
    completed_jobs_count = finalize_ready_refining_jobs(db)
    
    # Broadcast dashboard update if any jobs were completed
    if completed_jobs_count > 0:
        background_tasks.add_task(broadcast_dashboard, db)
    
    # Fetch active jobs
    active_jobs = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .all()
    )
    
    # Format response
    now = datetime.utcnow()
    return [
        _format_active_job(job, now)
        for job in active_jobs
    ]


@router.get("/history", response_model=List[Dict[str, Any]])
def get_refining_history(
    limit: int = Query(5, ge=1, le=100, description="Number of jobs to retrieve"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Retrieve completed refining jobs history with pagination.
    
    Args:
        limit: Maximum number of jobs to return (1-100)
        offset: Number of jobs to skip for pagination
        db: Database session dependency
        
    Returns:
        List of completed refining jobs ordered by completion date (newest first)
    """
    completed_jobs = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "DONE")
        .order_by(RefiningJob.completed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return [
        _format_history_job(job)
        for job in completed_jobs
    ]


@router.post("/start", response_model=RefiningJobResponse)
def start_refining_job(
    data: RefiningCreate,
    db: Session = Depends(get_db),
) -> Dict[str, int]:
    """
    Start a new refining job.
    
    Args:
        data: Refining job parameters including materials, quantities, and duration
        db: Database session dependency
        
    Returns:
        Dictionary containing the new job's ID
        
    Raises:
        HTTPException: If the refining job cannot be started
    """
    try:
        job_id = start_refining(
            input_material_id=data.input_material_id,
            output_material_id=data.output_material_id,
            input_quantity=data.input_quantity,
            output_quantity=data.output_quantity,
            duration_minutes=data.duration_minutes,
            db=db,
        )
        
        return {"job_id": job_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to start refining job: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_active_job(job: RefiningJob, current_time: datetime) -> Dict[str, Any]:
    """
    Format an active refining job for API response.
    
    Args:
        job: RefiningJob instance
        current_time: Current UTC datetime for calculating remaining time
        
    Returns:
        Formatted job dictionary with progress information
    """
    completion_time = job.started_at + timedelta(minutes=job.duration_minutes)
    remaining_seconds = max(0, int((completion_time - current_time).total_seconds()))
    
    return {
        "id": job.id,
        "material_name": job.output_material.name if job.output_material else "Unknown",
        "quantity": job.output_quantity,
        "remaining_seconds": remaining_seconds,
        "total_seconds": job.duration_minutes * 60,
    }


def _format_history_job(job: RefiningJob) -> Dict[str, Any]:
    """
    Format a completed refining job for API response.
    
    Args:
        job: RefiningJob instance
        
    Returns:
        Formatted job dictionary with completion details
    """
    return {
        "id": job.id,
        "material": job.output_material.name if job.output_material else "Unknown",
        "quantity": job.output_quantity,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "duration_minutes": job.duration_minutes,
    }