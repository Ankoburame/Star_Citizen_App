from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from database import SessionLocal
from models.run import Run
from models.stock_event import StockEvent

router = APIRouter()

class RunCreate(BaseModel):
    session_id: Optional[int] = None
    material_id: int
    quantity: int
    location: Optional[str] = None

@router.post("/run")
def create_run(data: RunCreate):
    db = SessionLocal()

    run = Run(
        session_id=data.session_id,
        material_id=data.material_id,
        raw_quantity=data.quantity,
        location=data.location
    )

    db.add(run)
    db.flush()  # 🔑 run.id est généré ici

    run_id = run.id  # ✅ on le stocke maintenant

    stock_event = StockEvent(
        material_id=data.material_id,
        quantity=data.quantity,
        event_type="PRODUCTION",
        reference_type="RUN",
        reference_id=run_id
    )

    db.add(stock_event)
    db.commit()
    db.close()

    return {
        "status": "OK",
        "run_id": run_id,
        "quantity_added": data.quantity
    }

