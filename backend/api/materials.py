from fastapi import APIRouter
from database import SessionLocal
from models.material import Material

router = APIRouter()

@router.get("/")
def list_materials():
    db = SessionLocal()
    materials = db.query(Material).all()
    db.close()

    return [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "unit": m.unit,
            "is_mineable": m.is_mineable,
            "is_salvage": m.is_salvage,
            "is_trade_good": m.is_trade_good,
        }
        for m in materials
    ]
