"""
Pricing service for Star Citizen App.
Manages price retrieval and caching for materials from various sources.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.market_price import MarketPrice
from services.uex.quantanium_service import refresh_quantanium_price

# Cache TTL for price data
PRICE_CACHE_TTL_HOURS = 12


def get_latest_sell_price(material_id: int, db: Session) -> Optional[float]:
    """
    Get the most recent sell price for a material from any source.
    
    This function returns the latest price regardless of source,
    suitable for trade and refining operations.
    
    Args:
        material_id: ID of the material
        db: Database session
        
    Returns:
        Latest sell price, or None if no price data exists
        
    Warning:
        For dashboard estimates, use get_latest_uex_sell_price() instead
        to ensure consistent pricing source.
    """
    price_record = (
        db.query(MarketPrice)
        .filter(MarketPrice.material_id == material_id)
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )
    
    return price_record.sell_price if price_record else None


def get_latest_uex_sell_price(material_id: int, db: Session) -> Optional[float]:
    """
    Get the most recent UEX sell price for a material.
    
    This function specifically returns UEX-sourced prices,
    providing consistent estimates for dashboard calculations.
    
    Args:
        material_id: ID of the material
        db: Database session
        
    Returns:
        Latest UEX sell price, or None if no UEX price data exists
    """
    price_record = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.material_id == material_id,
            MarketPrice.source == "UEX",
        )
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )
    
    return price_record.sell_price if price_record else None


def ensure_quantanium_price(db: Session) -> None:
    """
    Ensure Quantanium price data exists in the database.
    
    Checks if recent UEX price data exists and refreshes it if needed.
    Protected by TTL to avoid excessive API calls.
    
    Args:
        db: Database session
        
    Note:
        This function is typically called during application startup
        to ensure price data is available for initial requests.
    """
    # Check if we have recent price data
    if _has_recent_uex_price(db):
        return
    
    # Refresh price if cache is stale
    refresh_quantanium_price(db)


def _has_recent_uex_price(db: Session) -> bool:
    """
    Check if recent UEX price data exists within cache TTL.
    
    Args:
        db: Database session
        
    Returns:
        True if recent price data exists, False otherwise
    """
    cache_threshold = datetime.utcnow() - timedelta(hours=PRICE_CACHE_TTL_HOURS)
    
    latest_price = (
        db.query(MarketPrice)
        .filter(MarketPrice.source == "UEX")
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )
    
    if not latest_price:
        return False
    
    return latest_price.collected_at >= cache_threshold