"""
Dashboard service for Star Citizen App.
Provides dashboard statistics calculation and broadcasting functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.material import Material
from models.refining import RefiningJob
from models.stock import Stock
from models.market_price import MarketPrice


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    Calculate and retrieve dashboard statistics.
    
    Uses UEX prices for accurate stock valuation.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary containing stock totals, estimated values, and refining activity
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Recent completed refining jobs
    refining_history = _get_recent_refining_history(db, seven_days_ago)
    
    # Total stock quantity
    stock_total = _calculate_total_stock(db)
    
    # Estimated stock value using UEX prices
    estimated_stock_value = _calculate_stock_value_uex(db)
    
    # Active refining jobs count
    active_refining = _count_active_refining(db)
    
    return {
        "stock_total": int(stock_total),
        "estimated_stock_value": int(estimated_stock_value),
        "active_refining": active_refining,
        "refining_history": _format_refining_history(refining_history),
    }


def broadcast_dashboard(db: Session) -> None:
    """
    Broadcast dashboard updates to connected clients.
    
    This is currently a stub function for future WebSocket implementation.
    
    Args:
        db: Database session
    """
    # TODO: Implement WebSocket broadcasting when real-time updates are needed
    pass


# ============================================================================
# PRIVATE HELPER FUNCTIONS
# ============================================================================

def _get_recent_refining_history(
    db: Session, 
    since: datetime
) -> List[RefiningJob]:
    """
    Retrieve recent completed refining jobs.
    
    Args:
        db: Database session
        since: Datetime threshold for filtering jobs
        
    Returns:
        List of completed RefiningJob instances (max 5, newest first)
    """
    return (
        db.query(RefiningJob)
        .filter(
            RefiningJob.status == "DONE",
            RefiningJob.completed_at >= since,
        )
        .order_by(RefiningJob.completed_at.desc())
        .limit(5)
        .all()
    )


def _calculate_total_stock(db: Session) -> int:
    """
    Calculate total quantity of all stock items.
    
    Args:
        db: Database session
        
    Returns:
        Total stock quantity (0 if no stock exists)
    """
    return db.query(func.coalesce(func.sum(Stock.quantity), 0)).scalar()


def _calculate_stock_value_uex(db: Session) -> float:
    """
    Calculate total estimated value of all stock using UEX prices.
    
    This joins Stock with the latest UEX MarketPrice to get accurate valuations.
    Falls back to Material.sell_price if no UEX price exists.
    
    Args:
        db: Database session
        
    Returns:
        Total estimated stock value (0 if no stock exists)
    """
    # Subquery to get latest UEX price for each material
    latest_uex_price = (
        db.query(
            MarketPrice.material_id,
            func.max(MarketPrice.collected_at).label('max_date')
        )
        .filter(MarketPrice.source == 'UEX')
        .group_by(MarketPrice.material_id)
        .subquery()
    )
    
    # Join with actual prices
    uex_prices = (
        db.query(
            MarketPrice.material_id,
            MarketPrice.sell_price
        )
        .join(
            latest_uex_price,
            (MarketPrice.material_id == latest_uex_price.c.material_id) &
            (MarketPrice.collected_at == latest_uex_price.c.max_date)
        )
        .subquery()
    )
    
    # Calculate total value using UEX prices, fallback to Material.sell_price
    total_value = (
        db.query(
            func.coalesce(
                func.sum(
                    Stock.quantity * func.coalesce(
                        uex_prices.c.sell_price,
                        Material.sell_price
                    )
                ),
                0
            )
        )
        .join(Material, Stock.material_id == Material.id)
        .outerjoin(uex_prices, Stock.material_id == uex_prices.c.material_id)
        .scalar()
    )
    
    return float(total_value)


def _count_active_refining(db: Session) -> int:
    """
    Count currently running refining jobs.
    
    Args:
        db: Database session
        
    Returns:
        Number of active refining jobs
    """
    return (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .count()
    )


def _format_refining_history(jobs: List[RefiningJob]) -> List[Dict[str, Any]]:
    """
    Format refining jobs for API response.
    
    Args:
        jobs: List of RefiningJob instances
        
    Returns:
        List of formatted job dictionaries with material info and completion details
    """
    return [
        {
            "id": job.id,
            "material": job.output_material.name if job.output_material else "Unknown",
            "quantity": job.output_quantity,
            "ended_at": job.completed_at,
        }
        for job in jobs
    ]