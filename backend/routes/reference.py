"""
Router pour les données de référence (scan signatures, refineries, refining methods)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.scan_signature import ScanSignature
from models.refinery_bonus import RefineryBonus
from models.refining_method import RefiningMethod
from models.refinery import Refinery
from pydantic import BaseModel

router = APIRouter(prefix="/reference", tags=["reference"])

# ========================================
# SCHEMAS
# ========================================

class ScanSignatureResponse(BaseModel):
    id: int
    type: str
    category: str
    signatures: List[int]
    description: str | None

    class Config:
        from_attributes = True

class RefineryBonusResponse(BaseModel):
    id: int
    material_name: str
    bonus_percentage: int

    class Config:
        from_attributes = True

class RefineryResponse(BaseModel):
    id: int
    name: str
    system: str
    location: str
    is_active: bool
    bonuses: List[RefineryBonusResponse] = []

    class Config:
        from_attributes = True

class RefiningMethodResponse(BaseModel):
    id: int
    name: str
    time: str
    cost: str
    yield_rating: str
    description: str | None

    class Config:
        from_attributes = True

# ========================================
# ENDPOINTS
# ========================================

@router.get("/scan-signatures", response_model=List[ScanSignatureResponse])
async def get_scan_signatures(db: Session = Depends(get_db)):
    """
    Récupère toutes les signatures de scan
    """
    signatures = db.query(ScanSignature).all()
    return signatures

@router.get("/scan-signatures/{signature_id}", response_model=ScanSignatureResponse)
async def get_scan_signature(signature_id: int, db: Session = Depends(get_db)):
    """
    Récupère une signature spécifique
    """
    signature = db.query(ScanSignature).filter(ScanSignature.id == signature_id).first()
    if not signature:
        raise HTTPException(status_code=404, detail="Signature not found")
    return signature

@router.get("/scan-signatures/category/{category}", response_model=List[ScanSignatureResponse])
async def get_signatures_by_category(category: str, db: Session = Depends(get_db)):
    """
    Récupère les signatures par catégorie (Surface Deposit, Space Asteroid, etc.)
    """
    signatures = db.query(ScanSignature).filter(
        ScanSignature.category.ilike(f"%{category}%")
    ).all()
    return signatures

@router.get("/refineries", response_model=List[RefineryResponse])
async def get_refineries(db: Session = Depends(get_db)):
    """
    Récupère toutes les raffineries avec leurs bonus
    """
    refineries = db.query(Refinery).filter(Refinery.is_active == True).all()
    
    # Charger les bonus pour chaque raffinerie
    result = []
    for ref in refineries:
        bonuses = db.query(RefineryBonus).filter(
            RefineryBonus.refinery_id == ref.id
        ).all()
        
        ref_dict = {
            "id": ref.id,
            "name": ref.name,
            "system": ref.system,
            "location": ref.location,
            "is_active": ref.is_active,
            "bonuses": [
                {
                    "id": b.id,
                    "material_name": b.material_name,
                    "bonus_percentage": b.bonus_percentage
                }
                for b in bonuses
            ]
        }
        result.append(ref_dict)
    
    return result

@router.get("/refineries/{refinery_id}", response_model=RefineryResponse)
async def get_refinery(refinery_id: int, db: Session = Depends(get_db)):
    """
    Récupère une raffinerie spécifique avec ses bonus
    """
    refinery = db.query(Refinery).filter(Refinery.id == refinery_id).first()
    if not refinery:
        raise HTTPException(status_code=404, detail="Refinery not found")
    
    bonuses = db.query(RefineryBonus).filter(
        RefineryBonus.refinery_id == refinery_id
    ).all()
    
    return {
        "id": refinery.id,
        "name": refinery.name,
        "system": refinery.system,
        "location": refinery.location,
        "is_active": refinery.is_active,
        "bonuses": [
            {
                "id": b.id,
                "material_name": b.material_name,
                "bonus_percentage": b.bonus_percentage
            }
            for b in bonuses
        ]
    }

@router.get("/refineries/system/{system}", response_model=List[RefineryResponse])
async def get_refineries_by_system(system: str, db: Session = Depends(get_db)):
    """
    Récupère les raffineries d'un système spécifique
    """
    refineries = db.query(Refinery).filter(
        Refinery.system.ilike(f"%{system}%"),
        Refinery.is_active == True
    ).all()
    
    result = []
    for ref in refineries:
        bonuses = db.query(RefineryBonus).filter(
            RefineryBonus.refinery_id == ref.id
        ).all()
        
        ref_dict = {
            "id": ref.id,
            "name": ref.name,
            "system": ref.system,
            "location": ref.location,
            "is_active": ref.is_active,
            "bonuses": [
                {
                    "id": b.id,
                    "material_name": b.material_name,
                    "bonus_percentage": b.bonus_percentage
                }
                for b in bonuses
            ]
        }
        result.append(ref_dict)
    
    return result

@router.get("/refining-methods", response_model=List[RefiningMethodResponse])
async def get_refining_methods(db: Session = Depends(get_db)):
    """
    Récupère toutes les méthodes de raffinage
    """
    methods = db.query(RefiningMethod).all()
    return methods

@router.get("/refining-methods/{method_id}", response_model=RefiningMethodResponse)
async def get_refining_method(method_id: int, db: Session = Depends(get_db)):
    """
    Récupère une méthode spécifique
    """
    method = db.query(RefiningMethod).filter(RefiningMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Method not found")
    return method