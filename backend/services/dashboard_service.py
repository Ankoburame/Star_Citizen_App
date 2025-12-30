from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.refining import RefiningJob
from models.stock import Stock
from models.material import Material


def get_dashboard_stats(db: Session):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # === Historique des raffinages terminés
    refining_history = (
        db.query(RefiningJob)
        .filter(
            RefiningJob.status == "DONE",
            RefiningJob.completed_at >= seven_days_ago,
        )
        .order_by(RefiningJob.completed_at.desc())
        .limit(5)
        .all()
    )

    # === Stock total (AGRÉGÉ)
    stock_total = db.query(func.coalesce(func.sum(Stock.quantity), 0)).scalar()

    # === Valeur estimée (COMME AVANT)
    estimated_stock_value = (
    db.query(
        func.coalesce(
            func.sum(Stock.quantity * Material.sell_price),
            0
        )
    )
    .join(Material, Stock.material_id == Material.id)
    .scalar()
)


    # === Raffinages actifs
    active_refining = (
        db.query(RefiningJob)
        .filter(RefiningJob.status == "RUNNING")
        .count()
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

def broadcast_dashboard(db):
    # Stub volontaire – utilisé par api/refining
    return
