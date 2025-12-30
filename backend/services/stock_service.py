"""
Stock service for Star Citizen App.
Provides stock quantity queries and aggregations by material.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.stock_event import StockEvent


def get_stock_by_material(material_id: int, db: Session) -> int:
    """
    Calculate total stock quantity for a specific material.
    
    Aggregates all stock events (purchases, sales, production, consumption)
    to determine current stock level.
    
    Args:
        material_id: ID of the material to query
        db: Database session
        
    Returns:
        Total quantity in stock (0 if no stock exists)
        
    Note:
        This function sums all StockEvent quantities, where:
        - Positive values: purchases, production
        - Negative values: sales, consumption
    """
    total = (
        db.query(func.coalesce(func.sum(StockEvent.quantity), 0))
        .filter(StockEvent.material_id == material_id)
        .scalar()
    )
    
    return int(total)