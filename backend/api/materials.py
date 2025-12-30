"""
Materials API endpoint for Star Citizen App.
Provides access to the materials catalog with their properties.
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.material import Material

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
def list_materials(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Retrieve all available materials with their properties.
    
    Args:
        db: Database session dependency
        
    Returns:
        List of materials with their ID, name, category, unit, 
        and boolean flags (mineable, salvage, trade good)
    """
    materials = db.query(Material).all()
    
    return [
        _format_material(material)
        for material in materials
    ]


def _format_material(material: Material) -> Dict[str, Any]:
    """
    Format a material for API response.
    
    Args:
        material: Material instance
        
    Returns:
        Formatted material dictionary
    """
    return {
        "id": material.id,
        "name": material.name,
        "category": material.category,
        "unit": material.unit,
        "is_mineable": material.is_mineable,
        "is_salvage": material.is_salvage,
        "is_trade_good": material.is_trade_good,
    }