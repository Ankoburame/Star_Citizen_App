"""
Dashboard API endpoint - Global stats for all users.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, desc, text
from sqlalchemy.orm import Session

from database import get_db
from models.refining_job import RefiningJob
from models.inventory import Inventory

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve GLOBAL dashboard statistics (all users combined).
    No user filtering - shows organization-wide data.
    """
    
    # Total stock from Inventory table (all users)
    stock_total = db.query(func.coalesce(func.sum(Inventory.quantity), 0)).scalar()
    
    # Calculate estimated value
    estimated_stock_value = _calculate_stock_value(db)
    
    # Active refining jobs (all users, processing status)
    active_refining = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "processing")
        .count()
    )
    
    # Recent collected jobs (all users, last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    refining_history = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "collected")
        .filter(RefiningJob.collected_at >= seven_days_ago)
        .order_by(RefiningJob.collected_at.desc())
        .limit(5)
        .all()
    )
    
    formatted_history = [
        {
            "id": job.id,
            "material": ", ".join([m.material.name for m in job.materials]) if job.materials else "Unknown",
            "quantity": sum([m.quantity_refined for m in job.materials]) if job.materials else 0,
            "ended_at": job.collected_at or job.end_time,
        }
        for job in refining_history
    ]
    
    return {
        "stock_total": float(stock_total),
        "estimated_stock_value": float(estimated_stock_value),
        "active_refining": active_refining,
        "refining_history": formatted_history,
    }


def _calculate_stock_value(db: Session) -> float:
    """
    Calculate total stock value using market prices.
    Uses average sell price from market_prices table.
    """
    
    # Get all inventory with estimated prices
    result = db.execute(
        text("""
            SELECT 
                i.quantity,
                COALESCE(AVG(mp.sell_price), 0) as avg_price
            FROM inventory i
            LEFT JOIN market_prices mp ON i.material_id = mp.material_id
            WHERE i.quantity > 0
            GROUP BY i.id, i.quantity
        """)
    ).fetchall()
    
    total_value = sum(row[0] * row[1] for row in result)
    
    return total_value