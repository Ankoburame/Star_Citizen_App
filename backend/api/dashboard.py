"""
Dashboard API endpoint for Star Citizen App - VERSION DEBUG.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from database import get_db
from models.stock_event import StockEvent
from models.market_price import MarketPrice
from models.stock import Stock
from models.material import Material
from models.refining_job import RefiningJob

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def get_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve dashboard statistics with debugging."""
    
    # Total stock from Stock table
    stock_total = db.query(func.coalesce(func.sum(Stock.quantity), 0)).scalar()
    print(f"📊 Stock total: {stock_total}")

    # Calculate estimated value
    estimated_stock_value = _calculate_stock_value_debug(db)
    print(f"💰 Valeur estimée: {estimated_stock_value}")

    # Active refining
    active_refining = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .count()
    )

    # History
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    refining_history = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "DONE")
        .filter(RefiningJob.completed_at >= seven_days_ago)
        .order_by(RefiningJob.completed_at.desc())
        .limit(5)
        .all()
    )

    formatted_history = [
        {
            "id": job.id,
            "material": job.output_material.name if job.output_material else "Unknown",
            "quantity": job.output_quantity,
            "ended_at": job.completed_at,
        }
        for job in refining_history
    ]

    return {
        "stock_total": int(stock_total),
        "estimated_stock_value": int(estimated_stock_value),
        "active_refining": active_refining,
        "refining_history": formatted_history,
    }


def _calculate_stock_value_debug(db: Session) -> float:
    """Calculate stock value with detailed logging."""
    
    # Get all stock items with their materials
    stocks = db.query(Stock).all()
    print(f"\n🔍 Nombre d'items en stock: {len(stocks)}")
    
    total_value = 0.0
    
    for stock in stocks:
        if stock.quantity <= 0:
            continue
        
        # Get material name by querying separately
        material = db.query(Material).filter(Material.id == stock.material_id).first()
        material_name = material.name if material else "Unknown"
        print(f"\n📦 {material_name}: {stock.quantity} SCU")
        
        # Get latest UEX price
        latest_price_record = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.material_id == stock.material_id,
                MarketPrice.source == "UEX",
                MarketPrice.sell_price.isnot(None)
            )
            .order_by(desc(MarketPrice.collected_at))
            .first()
        )
        
        if latest_price_record:
            price = latest_price_record.sell_price
            value = stock.quantity * price
            total_value += value
            print(f"   💵 Prix UEX: {price:,.2f} aUEC")
            print(f"   💰 Valeur: {value:,.2f} aUEC")
        else:
            print(f"   ⚠️  Pas de prix UEX trouvé")
            
            # Fallback to Material.sell_price
            if material and material.sell_price:
                price = material.sell_price
                value = stock.quantity * price
                total_value += value
                print(f"   💵 Prix matériau (fallback): {price:,.2f} aUEC")
                print(f"   💰 Valeur: {value:,.2f} aUEC")
    
    print(f"\n💰 TOTAL: {total_value:,.2f} aUEC")
    return total_value