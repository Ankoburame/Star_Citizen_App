from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.uex.quantanium_service import refresh_quantanium_price

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/refresh/quantanium")
def refresh_quantanium(force: bool = False, db: Session = Depends(get_db)):
    refresh_quantanium_price(db, force=force)
    return {"status": "ok"}
