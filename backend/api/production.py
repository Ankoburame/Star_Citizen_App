"""
API endpoints pour le système de production (raffinerie, inventaire, ventes).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict

from database import get_db
from models.refinery import Refinery
from models.refining_job import RefiningJob, RefiningJobMaterial
from models.inventory import Inventory
from models.sale import Sale
from models.material import Material
from sqlalchemy import text  # ← AJOUTER EN HAUT DU FICHIER (ligne ~10)

router = APIRouter(prefix="/production", tags=["production"])


# ============================================================
# Pydantic Schemas
# ============================================================

class RefinerySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    system: str
    location: Optional[str]
    is_active: bool


class JobMaterialCreate(BaseModel):
    material_id: int
    quantity_refined: float


class JobMaterialSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    material_id: int
    material_name: str
    quantity_refined: float
    unit: str


class RefiningJobCreate(BaseModel):
    refinery_id: int
    job_type: str = "mining"  # 'mining' ou 'salvage'
    total_cost: float
    processing_time: int  # En minutes
    materials: List[JobMaterialCreate]
    notes: Optional[str] = None


class RefiningJobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    refinery_id: int
    refinery_name: str
    refinery_system: str
    job_type: str
    total_cost: float
    processing_time: int
    status: str
    start_time: datetime
    end_time: datetime
    collected_at: Optional[datetime]
    seconds_remaining: int
    progress_percentage: float
    notes: Optional[str]
    materials: List[JobMaterialSchema]


class InventorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    refinery_id: int
    refinery_name: str
    refinery_system: str
    material_id: int
    material_name: str
    quantity: float
    unit: str
    estimated_unit_price: float
    estimated_total_value: float
    last_updated: datetime


class SaleCreate(BaseModel):
    material_id: int
    refinery_source_id: int
    quantity_sold: float
    unit_price: float
    sale_location_id: Optional[int] = None
    refining_cost: float = 0
    notes: Optional[str] = None


class SaleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    material_id: int
    material_name: str
    quantity_sold: float
    unit: str
    unit_price: float
    total_revenue: float
    refining_cost: float
    profit: float
    profit_percentage: float
    sale_location_id: Optional[int]
    sale_location_name: Optional[str]
    refinery_source_id: Optional[int]
    refinery_source_name: Optional[str]
    sale_date: datetime
    notes: Optional[str]


# ============================================================
# ENDPOINTS: Refineries
# ============================================================

@router.get("/refineries", response_model=List[RefinerySchema])
def get_refineries(
    system: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Liste toutes les raffineries."""
    query = db.query(Refinery)
    
    if system:
        query = query.filter(Refinery.system == system)
    if active_only:
        query = query.filter(Refinery.is_active == True)
    
    return query.order_by(Refinery.system, Refinery.name).all()


# ============================================================
# ENDPOINTS: Refining Jobs
# ============================================================

@router.post("/jobs", response_model=RefiningJobSchema)
def create_refining_job(job: RefiningJobCreate, db: Session = Depends(get_db)):
    """Crée un nouveau job de raffinerie."""
    
    # Vérifier que la raffinerie existe
    refinery = db.query(Refinery).filter(Refinery.id == job.refinery_id).first()
    if not refinery:
        raise HTTPException(status_code=404, detail="Raffinerie non trouvée")
    
    # Calculer end_time
    end_time = datetime.utcnow() + timedelta(minutes=job.processing_time)
    
    # Créer le job
    new_job = RefiningJob(
        refinery_id=job.refinery_id,
        job_type=job.job_type,
        total_cost=job.total_cost,
        processing_time=job.processing_time,
        end_time=end_time,
        notes=job.notes
    )
    
    db.add(new_job)
    db.flush()  # Pour obtenir l'ID
    
    # Ajouter les matériaux
    for mat in job.materials:
        job_material = RefiningJobMaterial(
            job_id=new_job.id,
            material_id=mat.material_id,
            quantity_refined=mat.quantity_refined
        )
        db.add(job_material)
    
    db.commit()
    db.refresh(new_job)
    
    # Retourner avec relations chargées
    return _build_job_schema(new_job, db)


@router.get("/jobs", response_model=List[RefiningJobSchema])
def get_refining_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    refinery_id: Optional[int] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Liste les jobs de raffinerie."""
    query = db.query(RefiningJob).options(
        joinedload(RefiningJob.refinery),
        joinedload(RefiningJob.materials).joinedload(RefiningJobMaterial.material)
    )
    
    if status:
        query = query.filter(RefiningJob.status == status)
    if refinery_id:
        query = query.filter(RefiningJob.refinery_id == refinery_id)
    if job_type:
        query = query.filter(RefiningJob.job_type == job_type)
    
    jobs = query.order_by(RefiningJob.end_time).all()
    
    # Mettre à jour le status des jobs prêts
    for job in jobs:
        if job.check_and_update_status():
            db.commit()
    
    return [_build_job_schema(job, db) for job in jobs]


@router.get("/jobs/{job_id}", response_model=RefiningJobSchema)
def get_refining_job(job_id: int, db: Session = Depends(get_db)):
    """Récupère un job spécifique."""
    job = db.query(RefiningJob).filter(RefiningJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    
    # Mettre à jour le status si nécessaire
    if job.check_and_update_status():
        db.commit()
    
    return _build_job_schema(job, db)


@router.post("/jobs/{job_id}/collect")
def collect_refining_job(job_id: int, db: Session = Depends(get_db)):
    """Récupère un job terminé et transfère au stock."""
    job = db.query(RefiningJob).filter(RefiningJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    
    if job.status not in ["ready", "processing"]:
        raise HTTPException(status_code=400, detail="Job déjà collecté ou annulé")
    
    # Transférer les matériaux vers l'inventaire
    for job_mat in job.materials:
    # Chercher ou créer l'entrée d'inventaire
        inventory = db.query(Inventory).filter(
        Inventory.refinery_id == job.refinery_id,
        Inventory.material_id == job_mat.material_id,
        Inventory.user_id == job.user_id
    ).first()
    
    # Convertir quantité brute en SCU (÷ 100)
    from decimal import Decimal  # ← AJOUTER EN HAUT DU FICHIER (ligne ~10)

# Convertir quantité brute en SCU (÷ 100)
    quantity_scu = Decimal(str(job_mat.quantity_refined)) / Decimal('100')

    if inventory:
        inventory.add_quantity(quantity_scu)  # ✅ Decimal + Decimal OK
    else:
        inventory = Inventory(
            refinery_id=job.refinery_id,
            material_id=job_mat.material_id,
            user_id=job.user_id,
            quantity=quantity_scu  # ✅ Decimal OK
        )
        db.add(inventory)
    
    # Marquer le job comme collecté
    job.status = "collected"
    job.collected_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Job collecté avec succès", "job_id": job_id}


@router.delete("/jobs/{job_id}")
def cancel_refining_job(job_id: int, db: Session = Depends(get_db)):
    """Annule un job de raffinerie."""
    job = db.query(RefiningJob).filter(RefiningJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    
    if job.status == "collected":
        raise HTTPException(status_code=400, detail="Job déjà collecté")
    
    job.status = "cancelled"
    db.commit()
    
    return {"message": "Job annulé", "job_id": job_id}


# ============================================================
# ENDPOINTS: Inventory
# ============================================================

@router.get("/inventory", response_model=List[InventorySchema])
def get_inventory(
    refinery_id: Optional[int] = None,
    material_id: Optional[int] = None,
    min_quantity: float = 0,
    db: Session = Depends(get_db)
):
    """Liste l'inventaire."""
    query = db.query(Inventory).options(
        joinedload(Inventory.refinery),
        joinedload(Inventory.material)
    ).filter(Inventory.quantity > min_quantity)
    
    if refinery_id:
        query = query.filter(Inventory.refinery_id == refinery_id)
    if material_id:
        query = query.filter(Inventory.material_id == material_id)
    
    inventories = query.all()
    
    return [_build_inventory_schema(inv, db) for inv in inventories]


# ============================================================
# ENDPOINTS: Sales
# ============================================================

@router.post("/sales", response_model=SaleSchema)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Enregistre une vente."""
    
    # Vérifier l'inventaire
    inventory = db.query(Inventory).filter(
        Inventory.refinery_id == sale.refinery_source_id,
        Inventory.material_id == sale.material_id
    ).first()
    
    if not inventory or inventory.quantity < sale.quantity_sold:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    # Calculer le revenu total
    total_revenue = sale.quantity_sold * sale.unit_price
    
    # Créer la vente
    new_sale = Sale(
        material_id=sale.material_id,
        quantity_sold=sale.quantity_sold,
        unit_price=sale.unit_price,
        total_revenue=total_revenue,
        refining_cost=sale.refining_cost,
        sale_location_id=sale.sale_location_id,
        refinery_source_id=sale.refinery_source_id,
        notes=sale.notes
    )
    
    db.add(new_sale)
    
    # Retirer du stock
    inventory.remove_quantity(sale.quantity_sold)
    
    db.commit()
    db.refresh(new_sale)
    
    return _build_sale_schema(new_sale, db)


@router.get("/sales", response_model=List[SaleSchema])
def get_sales(
    material_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste les ventes."""
    query = db.query(Sale).options(
        joinedload(Sale.material),
        joinedload(Sale.sale_location),
        joinedload(Sale.refinery_source)
    )
    
    if material_id:
        query = query.filter(Sale.material_id == material_id)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    sales = query.order_by(Sale.sale_date.desc()).limit(limit).all()
    
    return [_build_sale_schema(s, db) for s in sales]


@router.get("/sales/stats")
def get_sales_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Statistiques globales des ventes."""
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    sales = query.all()
    
    if not sales:
        return {
            "total_sales": 0,
            "total_revenue": 0,
            "total_cost": 0,
            "total_profit": 0,
            "avg_profit_percentage": 0
        }
    
    total_revenue = sum(float(s.total_revenue) for s in sales)
    total_cost = sum(float(s.refining_cost or 0) for s in sales)
    total_profit = total_revenue - total_cost
    avg_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "total_sales": len(sales),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "avg_profit_percentage": round(avg_profit_pct, 2)
    }


# ============================================================
# Helper functions
# ============================================================

def _build_job_schema(job: RefiningJob, db: Session) -> RefiningJobSchema:
    """Construit le schema d'un job avec toutes les données."""
    materials = []
    for jm in job.materials:
        materials.append(JobMaterialSchema(
            id=jm.id,
            material_id=jm.material_id,
            material_name=jm.material.name,
            quantity_refined=float(jm.quantity_refined),
            unit=jm.unit
        ))
    
    return RefiningJobSchema(
        id=job.id,
        refinery_id=job.refinery_id,
        refinery_name=job.refinery.name,
        refinery_system=job.refinery.system,
        job_type=job.job_type,
        total_cost=float(job.total_cost),
        processing_time=job.processing_time,
        status=job.status,
        start_time=job.start_time,
        end_time=job.end_time,
        collected_at=job.collected_at,
        seconds_remaining=job.seconds_remaining,
        progress_percentage=job.progress_percentage,
        notes=job.notes,
        materials=materials
    )


def _build_inventory_schema(inv: Inventory, db: Session) -> InventorySchema:
    """Construit le schema d'inventaire avec prix estimé."""
    # Récupérer le prix de vente moyen depuis market_prices
    avg_price_query = db.execute(
        text("""
            SELECT AVG(sell_price) as avg_price
            FROM market_prices
            WHERE material_id = :mat_id AND sell_price IS NOT NULL
        """),
        {"mat_id": inv.material_id}
    ).fetchone()
    
    avg_price = float(avg_price_query[0]) if avg_price_query and avg_price_query[0] else 0.0
    total_value = float(inv.quantity) * avg_price
    
    return InventorySchema(
        id=inv.id,
        refinery_id=inv.refinery_id,
        refinery_name=inv.refinery.name,
        refinery_system=inv.refinery.system,
        material_id=inv.material_id,
        material_name=inv.material.name,
        quantity=float(inv.quantity),
        unit=inv.unit,
        estimated_unit_price=round(avg_price, 2),
        estimated_total_value=round(total_value, 2),
        last_updated=inv.last_updated
    )


def _build_sale_schema(sale: Sale, db: Session) -> SaleSchema:
    """Construit le schema de vente."""
    return SaleSchema(
        id=sale.id,
        material_id=sale.material_id,
        material_name=sale.material.name,
        quantity_sold=float(sale.quantity_sold),
        unit=sale.unit,
        unit_price=float(sale.unit_price),
        total_revenue=float(sale.total_revenue),
        refining_cost=float(sale.refining_cost or 0),
        profit=sale.profit,
        profit_percentage=sale.profit_percentage,
        sale_location_id=sale.sale_location_id,
        sale_location_name=sale.sale_location.name if sale.sale_location else None,
        refinery_source_id=sale.refinery_source_id,
        refinery_source_name=sale.refinery_source.name if sale.refinery_source else None,
        sale_date=sale.sale_date,
        notes=sale.notes
    )