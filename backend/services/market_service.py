"""
Market service for Star Citizen App.
Provides market price queries and best price calculations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from models.market_price import MarketPrice


def get_best_sell_price(material_id: int, db: Session) -> Optional[float]:
    """
    Get the best (highest) sell price for a material across all locations.
    
    Args:
        material_id: ID of the material to query
        db: Database session
        
    Returns:
        Highest sell price found, or None if no prices exist
    """
    price_record = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.material_id == material_id,
            MarketPrice.sell_price.isnot(None)
        )
        .order_by(MarketPrice.sell_price.desc())
        .first()
    )
    
    return price_record.sell_price if price_record else None