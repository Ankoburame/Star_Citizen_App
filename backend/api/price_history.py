"""
Price History API endpoints.

Provides historical price data for trend analysis and charts.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from database import get_db
from models.material import Material
from models.location import Location
from models.price_history import PriceHistory

from pydantic import BaseModel


# ============================================================================
# SCHEMAS
# ============================================================================

class PriceDataPoint(BaseModel):
    """Un point de données de prix à une date donnée."""
    date: datetime
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    location_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MaterialPriceHistory(BaseModel):
    """Historique des prix pour un matériau."""
    material_id: int
    material_name: str
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    data_points: List[PriceDataPoint]
    
    # Statistiques
    avg_sell_price: Optional[float] = None
    min_sell_price: Optional[float] = None
    max_sell_price: Optional[float] = None
    price_trend: Optional[float] = None  # Pourcentage de variation
    
    class Config:
        from_attributes = True


class PriceTrendSummary(BaseModel):
    """Résumé des tendances de prix."""
    material_id: int
    material_name: str
    current_avg_price: Optional[float] = None
    week_ago_avg_price: Optional[float] = None
    month_ago_avg_price: Optional[float] = None
    week_trend: Optional[float] = None  # % variation sur 7j
    month_trend: Optional[float] = None  # % variation sur 30j
    
    class Config:
        from_attributes = True


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/materials/{material_id}/history", response_model=MaterialPriceHistory)
def get_material_price_history(
    material_id: int,
    location_id: Optional[int] = Query(None, description="Filter by specific location"),
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des prix pour un matériau.
    
    Si location_id est fourni, retourne l'historique pour cette location uniquement.
    Sinon, retourne la moyenne des prix sur toutes les locations.
    """
    # Vérifier que le matériau existe
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Date limite
    since = datetime.utcnow() - timedelta(days=days)
    
    # Construire la requête
    query = db.query(PriceHistory).filter(
        and_(
            PriceHistory.material_id == material_id,
            PriceHistory.recorded_at >= since
        )
    )
    
    # Filtrer par location si spécifié
    location_name = None
    if location_id:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        query = query.filter(PriceHistory.location_id == location_id)
        location_name = location.name
    
    # Récupérer les données
    history = query.order_by(PriceHistory.recorded_at.asc()).all()
    
    if not history:
        # Pas d'historique, retourner structure vide
        return MaterialPriceHistory(
            material_id=material_id,
            material_name=material.name,
            location_id=location_id,
            location_name=location_name,
            data_points=[],
        )
    
    # Si location spécifique, données brutes
    if location_id:
        data_points = [
            PriceDataPoint(
                date=h.recorded_at,
                buy_price=h.buy_price,
                sell_price=h.sell_price,
                location_name=location_name
            )
            for h in history
        ]
    else:
        # Sinon, grouper par date et faire la moyenne
        # Grouper par jour
        daily_data = {}
        for h in history:
            date_key = h.recorded_at.date()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "buy_prices": [],
                    "sell_prices": []
                }
            
            if h.buy_price:
                daily_data[date_key]["buy_prices"].append(h.buy_price)
            if h.sell_price:
                daily_data[date_key]["sell_prices"].append(h.sell_price)
        
        # Calculer les moyennes
        data_points = []
        for date_key in sorted(daily_data.keys()):
            data = daily_data[date_key]
            
            avg_buy = (
                sum(data["buy_prices"]) / len(data["buy_prices"])
                if data["buy_prices"]
                else None
            )
            avg_sell = (
                sum(data["sell_prices"]) / len(data["sell_prices"])
                if data["sell_prices"]
                else None
            )
            
            data_points.append(
                PriceDataPoint(
                    date=datetime.combine(date_key, datetime.min.time()),
                    buy_price=avg_buy,
                    sell_price=avg_sell
                )
            )
    
    # Calculer les statistiques
    sell_prices = [dp.sell_price for dp in data_points if dp.sell_price]
    
    avg_sell = sum(sell_prices) / len(sell_prices) if sell_prices else None
    min_sell = min(sell_prices) if sell_prices else None
    max_sell = max(sell_prices) if sell_prices else None
    
    # Calculer la tendance (variation entre premier et dernier point)
    price_trend = None
    if len(sell_prices) >= 2:
        first_price = next((dp.sell_price for dp in data_points if dp.sell_price), None)
        last_price = next((dp.sell_price for dp in reversed(data_points) if dp.sell_price), None)
        
        if first_price and last_price and first_price > 0:
            price_trend = ((last_price - first_price) / first_price) * 100
    
    return MaterialPriceHistory(
        material_id=material_id,
        material_name=material.name,
        location_id=location_id,
        location_name=location_name,
        data_points=data_points,
        avg_sell_price=avg_sell,
        min_sell_price=min_sell,
        max_sell_price=max_sell,
        price_trend=price_trend,
    )


@router.get("/trends", response_model=List[PriceTrendSummary])
def get_price_trends(
    limit: int = Query(20, ge=1, le=100, description="Max number of materials"),
    sort_by: str = Query("week_trend", regex="^(week_trend|month_trend|material_name)$"),
    db: Session = Depends(get_db)
):
    """
    Récupère les tendances de prix pour tous les matériaux.
    
    Compare les prix actuels avec ceux d'il y a 7j et 30j.
    """
    # Dates de référence
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Récupérer tous les matériaux
    materials = db.query(Material).limit(limit).all()
    
    trends = []
    
    for material in materials:
        # Prix actuels (moyenne des dernières 24h)
        recent_prices = db.query(
            func.avg(PriceHistory.sell_price).label('avg_price')
        ).filter(
            and_(
                PriceHistory.material_id == material.id,
                PriceHistory.recorded_at >= now - timedelta(hours=24),
                PriceHistory.sell_price.isnot(None)
            )
        ).scalar()
        
        # Prix il y a 7 jours (moyenne de la journée)
        week_prices = db.query(
            func.avg(PriceHistory.sell_price).label('avg_price')
        ).filter(
            and_(
                PriceHistory.material_id == material.id,
                PriceHistory.recorded_at >= week_ago - timedelta(hours=12),
                PriceHistory.recorded_at <= week_ago + timedelta(hours=12),
                PriceHistory.sell_price.isnot(None)
            )
        ).scalar()
        
        # Prix il y a 30 jours
        month_prices = db.query(
            func.avg(PriceHistory.sell_price).label('avg_price')
        ).filter(
            and_(
                PriceHistory.material_id == material.id,
                PriceHistory.recorded_at >= month_ago - timedelta(hours=12),
                PriceHistory.recorded_at <= month_ago + timedelta(hours=12),
                PriceHistory.sell_price.isnot(None)
            )
        ).scalar()
        
        # Calculer les tendances
        week_trend = None
        if recent_prices and week_prices and week_prices > 0:
            week_trend = ((recent_prices - week_prices) / week_prices) * 100
        
        month_trend = None
        if recent_prices and month_prices and month_prices > 0:
            month_trend = ((recent_prices - month_prices) / month_prices) * 100
        
        trends.append(
            PriceTrendSummary(
                material_id=material.id,
                material_name=material.name,
                current_avg_price=recent_prices,
                week_ago_avg_price=week_prices,
                month_ago_avg_price=month_prices,
                week_trend=week_trend,
                month_trend=month_trend,
            )
        )
    
    # Trier selon le paramètre
    if sort_by == "week_trend":
        trends.sort(key=lambda t: t.week_trend or 0, reverse=True)
    elif sort_by == "month_trend":
        trends.sort(key=lambda t: t.month_trend or 0, reverse=True)
    else:  # material_name
        trends.sort(key=lambda t: t.material_name)
    
    return trends


@router.get("/stats")
def get_history_stats(db: Session = Depends(get_db)):
    """
    Récupère des statistiques sur l'historique des prix.
    """
    # Total d'entrées
    total = db.query(func.count(PriceHistory.id)).scalar()
    
    # Matériaux avec historique
    materials_count = db.query(
        func.count(func.distinct(PriceHistory.material_id))
    ).scalar()
    
    # Locations avec historique
    locations_count = db.query(
        func.count(func.distinct(PriceHistory.location_id))
    ).scalar()
    
    # Premier et dernier snapshot
    first = db.query(func.min(PriceHistory.recorded_at)).scalar()
    last = db.query(func.max(PriceHistory.recorded_at)).scalar()
    
    # Nombre de jours de couverture
    days_coverage = 0
    if first and last:
        days_coverage = (last - first).days
    
    return {
        "total_entries": total,
        "materials_with_history": materials_count,
        "locations_with_history": locations_count,
        "first_snapshot": first,
        "last_snapshot": last,
        "days_coverage": days_coverage,
    }