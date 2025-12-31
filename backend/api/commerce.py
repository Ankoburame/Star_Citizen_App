# ============================================================
# API: Commerce Module - Cargo Runs Endpoints
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models.models import CargoRun
from database import Base

router = APIRouter(prefix="/commerce", tags=["commerce"])


# ============================================================
# SCHEMAS
# ============================================================

class CargoRunCreate(BaseModel):
    commodity_name: str
    buy_location: str
    sell_location: str
    quantity: int
    buy_price: float
    sell_price: float
    notes: Optional[str] = None


class CargoRunResponse(BaseModel):
    id: int
    commodity_name: str
    buy_location: str
    sell_location: str
    quantity: int
    buy_price: float
    sell_price: float
    total_investment: float
    expected_profit: float
    status: str
    created_at: str
    delivered_at: Optional[str]
    notes: Optional[str]


class CommerceStats(BaseModel):
    total_runs: int
    active_runs: int
    delivered_runs: int
    total_profit: float
    total_investment: float
    roi_percentage: float


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/runs", response_model=CargoRunResponse)
def create_cargo_run(cargo_run: CargoRunCreate, db: Session = Depends(get_db)):
    """
    Créer un nouveau cargo run
    """
    # Calculs automatiques
    total_investment = cargo_run.quantity * cargo_run.buy_price
    expected_profit = (cargo_run.sell_price - cargo_run.buy_price) * cargo_run.quantity
    
    new_run = CargoRun(
        commodity_name=cargo_run.commodity_name,
        buy_location=cargo_run.buy_location,
        sell_location=cargo_run.sell_location,
        quantity=cargo_run.quantity,
        buy_price=cargo_run.buy_price,
        sell_price=cargo_run.sell_price,
        total_investment=total_investment,
        expected_profit=expected_profit,
        status="active",
        notes=cargo_run.notes
    )
    
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    
    return new_run.to_dict()


@router.get("/runs", response_model=List[CargoRunResponse])
def get_cargo_runs(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des cargo runs
    """
    query = db.query(CargoRun)
    
    if status:
        query = query.filter(CargoRun.status == status)
    
    runs = query.order_by(CargoRun.created_at.desc()).limit(limit).all()
    
    return [run.to_dict() for run in runs]


@router.get("/runs/{run_id}", response_model=CargoRunResponse)
def get_cargo_run(run_id: int, db: Session = Depends(get_db)):
    """
    Récupérer un cargo run spécifique
    """
    run = db.query(CargoRun).filter(CargoRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Cargo run not found")
    
    return run.to_dict()


@router.post("/runs/{run_id}/deliver")
def deliver_cargo_run(run_id: int, db: Session = Depends(get_db)):
    """
    Marquer un cargo run comme livré
    """
    run = db.query(CargoRun).filter(CargoRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Cargo run not found")
    
    if run.status != "active":
        raise HTTPException(status_code=400, detail="Cargo run is not active")
    
    run.status = "delivered"
    run.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(run)
    
    return run.to_dict()


@router.post("/runs/{run_id}/cancel")
def cancel_cargo_run(run_id: int, db: Session = Depends(get_db)):
    """
    Annuler un cargo run
    """
    run = db.query(CargoRun).filter(CargoRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Cargo run not found")
    
    if run.status != "active":
        raise HTTPException(status_code=400, detail="Cargo run is not active")
    
    run.status = "cancelled"
    
    db.commit()
    db.refresh(run)
    
    return run.to_dict()


@router.delete("/runs/{run_id}")
def delete_cargo_run(run_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un cargo run
    """
    run = db.query(CargoRun).filter(CargoRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Cargo run not found")
    
    db.delete(run)
    db.commit()
    
    return {"message": "Cargo run deleted successfully"}


@router.get("/stats", response_model=CommerceStats)
def get_commerce_stats(db: Session = Depends(get_db)):
    """
    Récupérer les statistiques du commerce
    """
    total_runs = db.query(func.count(CargoRun.id)).scalar() or 0
    active_runs = db.query(func.count(CargoRun.id)).filter(CargoRun.status == "active").scalar() or 0
    delivered_runs = db.query(func.count(CargoRun.id)).filter(CargoRun.status == "delivered").scalar() or 0
    
    # Profit total des runs livrés
    delivered_profit = db.query(func.sum(CargoRun.expected_profit)).filter(
        CargoRun.status == "delivered"
    ).scalar() or 0
    
    # Investment total des runs livrés
    delivered_investment = db.query(func.sum(CargoRun.total_investment)).filter(
        CargoRun.status == "delivered"
    ).scalar() or 0
    
    # ROI
    roi_percentage = (delivered_profit / delivered_investment * 100) if delivered_investment > 0 else 0
    
    return {
        "total_runs": total_runs,
        "active_runs": active_runs,
        "delivered_runs": delivered_runs,
        "total_profit": delivered_profit,
        "total_investment": delivered_investment,
        "roi_percentage": roi_percentage
    }