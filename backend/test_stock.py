from database import SessionLocal
from models.stock_event import StockEvent
from services.stock_service import get_stock_by_material

db = SessionLocal()

# Entrée stock (production)
db.add(StockEvent(
    material_id=1,
    quantity=500,
    event_type="PRODUCTION",
    reference_type="RUN",
    reference_id=1
))

# Sortie stock (vente)
db.add(StockEvent(
    material_id=1,
    quantity=-200,
    event_type="SELL",
    reference_type="COMMERCE",
    reference_id=1
))

db.commit()
db.close()

print("Stock final:", get_stock_by_material(1))
