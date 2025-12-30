"""
Pricing API endpoint for Star Citizen App.
Handles price updates and refresh operations for all materials.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.uex.uex_service import (
    refresh_all_prices,
    refresh_single_material,
    get_material_price_history,
)

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/refresh/all")
def refresh_all_materials(
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Rafraîchit les prix de TOUS les matériaux depuis UEX.
    
    Cette opération peut prendre du temps (plusieurs secondes).
    Utilise background_tasks pour ne pas bloquer si nécessaire.
    
    Args:
        force: Si True, force le refresh même si le cache est valide
        background_tasks: FastAPI background tasks
        db: Session de base de données
        
    Returns:
        Statistiques du refresh (updated, skipped, errors)
    """
    try:
        stats = refresh_all_prices(db, force=force)
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh prices: {str(e)}"
        )


@router.post("/refresh/{material_id}")
def refresh_material_price(
    material_id: int,
    force: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Rafraîchit le prix d'un seul matériau.
    
    Args:
        material_id: ID du matériau
        force: Si True, force le refresh
        db: Session de base de données
        
    Returns:
        Statut de l'opération
    """
    try:
        updated = refresh_single_material(db, material_id, force=force)
        return {
            "status": "success",
            "updated": updated
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh price: {str(e)}"
        )


@router.get("/history/{material_id}")
def get_price_history(
    material_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Récupère l'historique des prix d'un matériau.
    
    Args:
        material_id: ID du matériau
        days: Nombre de jours d'historique (défaut: 30)
        db: Session de base de données
        
    Returns:
        Liste des prix historiques
    """
    try:
        history = get_material_price_history(db, material_id, days)
        
        return {
            "material_id": material_id,
            "history": [
                {
                    "date": price.collected_at.isoformat(),
                    "sell_price": price.sell_price,
                    "buy_price": price.buy_price,
                    "location": price.location,
                }
                for price in history
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get price history: {str(e)}"
        )