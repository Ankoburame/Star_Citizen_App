"""
Pricing API endpoint for Star Citizen App.
Handles price updates and refresh operations for various materials.
"""

from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.uex.quantanium_service import refresh_quantanium_price

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/refresh/quantanium", response_model=Dict[str, str])
def refresh_quantanium(
    force: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Refresh Quantanium price from external source.
    
    This endpoint triggers a price update for Quantanium material,
    optionally forcing a refresh even if recent data exists.
    
    Args:
        force: If True, force refresh even if cache is valid
        db: Database session dependency
        
    Returns:
        Status dictionary indicating success
    """
    refresh_quantanium_price(db, force=force)
    
    return {"status": "ok"}