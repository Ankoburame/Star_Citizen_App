from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import get_db
from models.refining import RefiningJob
from models.stock_event import StockEvent

router = APIRouter()

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    stock_total = (
        db.query(func.coalesce(func.sum(StockEvent.quantity), 0))
        .filter(StockEvent.quantity > 0)
        .scalar()
    )

    estimated_stock_value = (
        db.query(func.coalesce(func.sum(StockEvent.total_value), 0))
        .filter(StockEvent.total_value > 0)
        .scalar()
    )

    active_refining = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .count()
    )

    refining_history = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "DONE")
        .filter(
            RefiningJob.completed_at
            >= datetime.utcnow() - timedelta(days=7)
        )
        .order_by(RefiningJob.completed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "stock_total": int(stock_total),
        "estimated_stock_value": int(estimated_stock_value),
        "active_refining": active_refining,
        "refining_history": [
            {
                "id": job.id,
                "material": job.output_material.name if job.output_material else "Unknown",
                "quantity": job.output_quantity,
                "ended_at": job.completed_at,
            }
            for job in refining_history
        ],
    }
