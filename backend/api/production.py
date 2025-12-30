"""
Production API endpoint for Star Citizen App.
Handles production runs and stock event tracking.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models.run import Run
from models.stock_event import StockEvent

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class RunCreate(BaseModel):
    """Schema for creating a production run."""
    
    session_id: Optional[int] = Field(None, description="Optional session ID")
    material_id: int = Field(..., gt=0, description="Material being produced")
    quantity: int = Field(..., gt=0, description="Quantity produced")
    location: Optional[str] = Field(None, description="Production location")


class RunResponse(BaseModel):
    """Response schema for production run creation."""
    
    status: str
    run_id: int
    quantity_added: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/run", response_model=RunResponse)
def create_run(
    data: RunCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new production run and update stock.
    
    This endpoint creates a production run record and automatically
    creates a corresponding stock event to track the inventory change.
    
    Args:
        data: Production run parameters
        db: Database session dependency
        
    Returns:
        Dictionary containing status, run ID, and quantity added
        
    Raises:
        HTTPException: If the production run cannot be created
    """
    try:
        # Create production run
        run = _create_production_run(db, data)
        
        # Create corresponding stock event
        _create_stock_event(db, run.id, data.material_id, data.quantity)
        
        db.commit()
        
        return {
            "status": "OK",
            "run_id": run.id,
            "quantity_added": data.quantity
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create production run: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _create_production_run(db: Session, data: RunCreate) -> Run:
    """
    Create a production run record.
    
    Args:
        db: Database session
        data: Production run parameters
        
    Returns:
        Created Run instance with generated ID
    """
    run = Run(
        session_id=data.session_id,
        material_id=data.material_id,
        raw_quantity=data.quantity,
        location=data.location
    )
    
    db.add(run)
    db.flush()  # Generate run.id
    
    return run


def _create_stock_event(
    db: Session,
    run_id: int,
    material_id: int,
    quantity: int
) -> None:
    """
    Create a stock event for the production run.
    
    Args:
        db: Database session
        run_id: ID of the production run
        material_id: Material being produced
        quantity: Quantity produced
    """
    stock_event = StockEvent(
        material_id=material_id,
        quantity=quantity,
        event_type="PRODUCTION",
        reference_type="RUN",
        reference_id=run_id
    )
    
    db.add(stock_event)