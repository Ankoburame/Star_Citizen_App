from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.stock import Stock
from models.stock_event import StockEvent
from services.trade_service import create_trade_run
from services.pricing_service import get_latest_sell_price

router = APIRouter()


# =========================
# SCHEMA
# =========================
class TradeCreate(BaseModel):
    material_id: int
    quantity: int
    buy_price: float
    sell_price: float
    buy_location: str
    sell_location: str


# =========================
# FULL TRADE RUN (SIMU)
# =========================
@router.post("/run")
def trade_run(data: TradeCreate):
    return create_trade_run(
        material_id=data.material_id,
        quantity=data.quantity,
        buy_price=data.buy_price,
        sell_price=data.sell_price,
        buy_location=data.buy_location,
        sell_location=data.sell_location,
    )


# =========================
# BUY
# =========================
@router.post("/buy")
def buy_material(
    material_id: int,
    quantity: int,
    db: Session = Depends(get_db),
):
    price = get_latest_sell_price(material_id, db)
    if price is None:
        raise HTTPException(status_code=400, detail="Prix indisponible")

    total = price * quantity

    # Stock
    stock = db.query(Stock).filter_by(material_id=material_id).first()
    if stock:
        stock.quantity += quantity
    else:
        db.add(Stock(material_id=material_id, quantity=quantity))

    # Event
    db.add(
        StockEvent(
            material_id=material_id,
            quantity=quantity,
            total_value=-total,
            event_type="BUY",
        )
    )

    db.commit()

    return {
        "material_id": material_id,
        "quantity": quantity,
        "unit_price": price,
        "total_cost": total,
    }


# =========================
# SELL
# =========================
@router.post("/sell")
def sell_material(
    material_id: int,
    quantity: int,
    db: Session = Depends(get_db),
):
    stock = db.query(Stock).filter_by(material_id=material_id).first()
    if not stock or stock.quantity < quantity:
        raise HTTPException(status_code=400, detail="Stock insuffisant")

    price = get_latest_sell_price(material_id, db)
    if price is None:
        raise HTTPException(status_code=400, detail="Prix indisponible")

    total = price * quantity

    stock.quantity -= quantity

    db.add(
        StockEvent(
            material_id=material_id,
            quantity=quantity,
            total_value=total,
            event_type="SELL",
        )
    )

    db.commit()

    return {
        "material_id": material_id,
        "quantity": quantity,
        "unit_price": price,
        "total_gain": total,
    }
