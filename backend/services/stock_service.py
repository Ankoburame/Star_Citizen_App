from sqlalchemy import func
from database import SessionLocal
from models.stock_event import StockEvent

def get_stock_by_material(material_id: int) -> int:
    db = SessionLocal()
    total = db.query(func.coalesce(func.sum(StockEvent.quantity), 0))\
              .filter(StockEvent.material_id == material_id)\
              .scalar()
    db.close()
    return total
