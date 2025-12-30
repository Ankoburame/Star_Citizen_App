from database import SessionLocal
from models.trade_run import TradeRun
from models.stock_event import StockEvent

def create_trade_run(
    material_id: int,
    quantity: int,
    buy_price: float,
    sell_price: float,
    buy_location: str,
    sell_location: str
):
    db = SessionLocal()

    trade = TradeRun(
        material_id=material_id,
        quantity=quantity,
        buy_price=buy_price,
        sell_price=sell_price,
        buy_location=buy_location,
        sell_location=sell_location
    )

    db.add(trade)
    db.flush()
    trade_id = trade.id

    # 🔺 Achat → stock +
    buy_event = StockEvent(
        material_id=material_id,
        quantity=quantity,
        event_type="BUY",
        reference_type="TRADE",
        reference_id=trade_id
    )

    # 🔻 Vente → stock -
    sell_event = StockEvent(
        material_id=material_id,
        quantity=-quantity,
        event_type="SELL",
        reference_type="TRADE",
        reference_id=trade_id
    )

    db.add(buy_event)
    db.add(sell_event)
    db.commit()
    db.close()

    profit = (sell_price - buy_price) * quantity

    return {
        "trade_id": trade_id,
        "profit": profit
    }
