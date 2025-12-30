"""
Refining service for Star Citizen App.
Handles the creation and tracking of material refining jobs.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from models.refining import RefiningJob
from models.stock_event import StockEvent


def start_refining(
    input_material_id: int,
    output_material_id: int,
    input_quantity: int,
    output_quantity: int,
    duration_minutes: int,
    db: Session,
) -> int:
    """
    Start a new refining job and consume input materials.
    
    Creates a refining job record and generates a stock event to track
    the consumption of raw materials. The job will be marked as "RUNNING"
    until its duration elapses.
    
    Args:
        input_material_id: ID of the raw material being consumed
        output_material_id: ID of the refined material being produced
        input_quantity: Amount of raw material to consume
        output_quantity: Amount of refined material to produce
        duration_minutes: Duration of the refining process
        db: Database session
        
    Returns:
        ID of the created refining job
        
    Note:
        The consumption event is recorded with zero value to maintain
        financial neutrality during the refining process.
    """
    # Create refining job
    job = _create_refining_job(
        db=db,
        input_material_id=input_material_id,
        output_material_id=output_material_id,
        input_quantity=input_quantity,
        output_quantity=output_quantity,
        duration_minutes=duration_minutes,
    )
    
    # Record material consumption
    _record_material_consumption(
        db=db,
        job_id=job.id,
        material_id=input_material_id,
        quantity=input_quantity,
    )
    
    return job.id


def _create_refining_job(
    db: Session,
    input_material_id: int,
    output_material_id: int,
    input_quantity: int,
    output_quantity: int,
    duration_minutes: int,
) -> RefiningJob:
    """
    Create a new refining job record.
    
    Args:
        db: Database session
        input_material_id: Raw material ID
        output_material_id: Refined material ID
        input_quantity: Raw material quantity
        output_quantity: Refined material quantity
        duration_minutes: Refining duration
        
    Returns:
        Created RefiningJob instance with generated ID
    """
    job = RefiningJob(
        input_material_id=input_material_id,
        output_material_id=output_material_id,
        input_quantity=input_quantity,
        output_quantity=output_quantity,
        duration_minutes=duration_minutes,
        started_at=datetime.utcnow(),
        status="RUNNING",
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


def _record_material_consumption(
    db: Session,
    job_id: int,
    material_id: int,
    quantity: int,
) -> None:
    """
    Record the consumption of raw materials for a refining job.
    
    Creates a stock event with zero financial value to track
    material consumption without affecting financial totals.
    
    Args:
        db: Database session
        job_id: ID of the refining job
        material_id: ID of the consumed material
        quantity: Quantity consumed (will be recorded as negative)
    """
    consume_event = StockEvent(
        material_id=material_id,
        quantity=-quantity,
        unit_price=0.0,
        total_value=0.0,
        event_type="REFINING_CONSUME",
        reference_type="REFINING",
        reference_id=job_id,
    )
    
    db.add(consume_event)
    db.commit()