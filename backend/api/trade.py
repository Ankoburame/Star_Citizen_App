"""
Trade API endpoint for Star Citizen App.
Handles buying, selling, and trade run simulations.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models.stock import Stock
from models.stock_event import StockEvent
from services.pricing_service import get_latest_sell_price
from services.trade_service import create_trade_run

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class TradeCreate(BaseModel):
    """Schema for creating a trade run simulation."""
    
    material_id: int = Field(..., gt=0, description="Material to trade")
    quantity: int = Field(..., gt=0, description="Quantity to trade")
    buy_price: float = Field(..., gt=0, description="Purchase price per unit")
    sell_price: float = Field(..., gt=0, description="Selling price per unit")
    buy_location: str = Field(..., description="Purchase location")
    sell_location: str = Field(..., description="Selling location")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/run")
def trade_run(data: TradeCreate) -> Dict[str, Any]:
    """
    Simulate a complete trade run without affecting actual stock.
    
    Calculates profit/loss and provides trade analysis without
    committing changes to the database.
    
    Args:
        data: Trade run parameters
        
    Returns:
        Trade simulation results including costs, revenue, and profit
    """
    return create_trade_run(
        material_id=data.material_id,
        quantity=data.quantity,
        buy_price=data.buy_price,
        sell_price=data.sell_price,
        buy_location=data.buy_location,
        sell_location=data.sell_location,
    )


@router.post("/buy")
def buy_material(
    material_id: int,
    quantity: int,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Purchase material and add to stock.
    
    Uses the latest available sell price to calculate total cost
    and creates a stock event for tracking.
    
    Args:
        material_id: ID of the material to purchase
        quantity: Quantity to purchase
        db: Database session dependency
        
    Returns:
        Purchase details including unit price and total cost
        
    Raises:
        HTTPException: If price is unavailable
    """
    # Get current price
    price = get_latest_sell_price(material_id, db)
    if price is None:
        raise HTTPException(
            status_code=400,
            detail="Price unavailable for this material"
        )
    
    total_cost = price * quantity
    
    # Update stock
    _update_stock_for_purchase(db, material_id, quantity)
    
    # Create stock event
    _create_purchase_event(db, material_id, quantity, total_cost)
    
    db.commit()
    
    return {
        "material_id": material_id,
        "quantity": quantity,
        "unit_price": price,
        "total_cost": total_cost,
    }


@router.post("/sell")
def sell_material(
    material_id: int,
    quantity: int,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Sell material from stock.
    
    Validates sufficient stock exists, uses latest sell price,
    and creates a stock event for tracking.
    
    Args:
        material_id: ID of the material to sell
        quantity: Quantity to sell
        db: Database session dependency
        
    Returns:
        Sale details including unit price and total gain
        
    Raises:
        HTTPException: If insufficient stock or price unavailable
    """
    # Validate stock availability
    stock = db.query(Stock).filter_by(material_id=material_id).first()
    if not stock or stock.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock for this sale"
        )
    
    # Get current price
    price = get_latest_sell_price(material_id, db)
    if price is None:
        raise HTTPException(
            status_code=400,
            detail="Price unavailable for this material"
        )
    
    total_gain = price * quantity
    
    # Update stock
    stock.quantity -= quantity
    
    # Create stock event
    _create_sale_event(db, material_id, quantity, total_gain)
    
    db.commit()
    
    return {
        "material_id": material_id,
        "quantity": quantity,
        "unit_price": price,
        "total_gain": total_gain,
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _update_stock_for_purchase(
    db: Session,
    material_id: int,
    quantity: int
) -> None:
    """
    Update stock for a purchase, creating stock record if needed.
    
    Args:
        db: Database session
        material_id: Material being purchased
        quantity: Quantity being added
    """
    stock = db.query(Stock).filter_by(material_id=material_id).first()
    
    if stock:
        stock.quantity += quantity
    else:
        db.add(Stock(material_id=material_id, quantity=quantity))


def _create_purchase_event(
    db: Session,
    material_id: int,
    quantity: int,
    total_cost: float
) -> None:
    """
    Create a stock event for a purchase.
    
    Args:
        db: Database session
        material_id: Material being purchased
        quantity: Quantity purchased
        total_cost: Total cost (stored as negative value)
    """
    db.add(
        StockEvent(
            material_id=material_id,
            quantity=quantity,
            total_value=-total_cost,
            event_type="BUY",
        )
    )


def _create_sale_event(
    db: Session,
    material_id: int,
    quantity: int,
    total_gain: float
) -> None:
    """
    Create a stock event for a sale.
    
    Args:
        db: Database session
        material_id: Material being sold
        quantity: Quantity sold
        total_gain: Total revenue from sale
    """
    db.add(
        StockEvent(
            material_id=material_id,
            quantity=quantity,
            total_value=total_gain,
            event_type="SELL",
        )
    )