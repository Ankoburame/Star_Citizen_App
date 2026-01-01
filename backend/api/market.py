"""
Market API routes for Star Citizen App.

Provides endpoints for:
- Listing all materials with their market prices
- Getting detailed price information for a specific material
- Finding best buy/sell locations
- Price comparison across locations
- Market trends and statistics
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.material import Material
from models.location import Location
from models.market_price import MarketPrice

# Pydantic schemas
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS (Response Models)
# ============================================================================

class LocationInfo(BaseModel):
    """Information de base sur une location."""
    id: Optional[int] = None
    name: str
    code: Optional[str] = None
    system: Optional[str] = None
    planet: Optional[str] = None
    location_type: Optional[str] = None
    full_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class PriceInfo(BaseModel):
    """Information sur un prix à une location donnée."""
    location: LocationInfo
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MaterialMarketInfo(BaseModel):
    """Information complète sur un matériau et ses prix."""
    id: int
    name: str
    category: str
    unit: str
    is_mineable: bool
    is_salvage: bool
    is_trade_good: bool
    
    # Statistiques de prix
    avg_buy_price: Optional[float] = None
    avg_sell_price: Optional[float] = None
    min_buy_price: Optional[float] = None
    max_sell_price: Optional[float] = None
    
    # Meilleurs emplacements
    best_buy_location: Optional[LocationInfo] = None
    best_sell_location: Optional[LocationInfo] = None
    
    # Nombre de locations disponibles
    available_at: int = 0
    
    class Config:
        from_attributes = True


class MaterialDetailedMarket(BaseModel):
    """Information détaillée avec tous les prix par location."""
    material: MaterialMarketInfo
    prices: List[PriceInfo]
    
    class Config:
        from_attributes = True


class TradeRoute(BaseModel):
    """Information sur une route commerciale profitable."""
    material_name: str
    material_id: int
    
    buy_location: LocationInfo
    buy_price: float
    
    sell_location: LocationInfo
    sell_price: float
    
    profit_per_unit: float
    profit_margin_percent: float
    
    class Config:
        from_attributes = True


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/materials", response_model=List[MaterialMarketInfo])
def get_all_materials_with_prices(
    category: Optional[str] = Query(None, description="Filter by category: mineral, salvage, trade"),
    is_mineable: Optional[bool] = Query(None, description="Filter mineable materials"),
    is_salvage: Optional[bool] = Query(None, description="Filter salvage materials"),
    is_trade_good: Optional[bool] = Query(None, description="Filter trade goods"),
    min_price: Optional[float] = Query(None, description="Minimum average sell price"),
    max_price: Optional[float] = Query(None, description="Maximum average sell price"),
    db: Session = Depends(get_db)
):
    """
    Liste tous les matériaux avec leurs informations de prix.
    
    Retourne les statistiques de prix (min, max, avg) et les meilleurs emplacements
    pour acheter/vendre chaque matériau.
    """
    # Construction de la requête de base
    query = db.query(Material)
    
    # Filtres
    if category:
        query = query.filter(Material.category == category)
    if is_mineable is not None:
        query = query.filter(Material.is_mineable == is_mineable)
    if is_salvage is not None:
        query = query.filter(Material.is_salvage == is_salvage)
    if is_trade_good is not None:
        query = query.filter(Material.is_trade_good == is_trade_good)
    
    materials = query.all()
    
    result = []
    
    for material in materials:
        # Récupérer les prix pour ce matériau
        prices = db.query(MarketPrice).filter(
            MarketPrice.material_id == material.id
        ).options(
            joinedload(MarketPrice.location_obj)
        ).all()
        
        if not prices:
            # Pas de prix disponibles
            result.append(MaterialMarketInfo(
                id=material.id,
                name=material.name,
                category=material.category,
                unit=material.unit,
                is_mineable=material.is_mineable,
                is_salvage=material.is_salvage,
                is_trade_good=material.is_trade_good,
                available_at=0,
            ))
            continue
        
        # Calculer les statistiques
        buy_prices = [p.buy_price for p in prices if p.buy_price]
        sell_prices = [p.sell_price for p in prices if p.sell_price]
        
        avg_buy = sum(buy_prices) / len(buy_prices) if buy_prices else None
        avg_sell = sum(sell_prices) / len(sell_prices) if sell_prices else None
        min_buy = min(buy_prices) if buy_prices else None
        max_sell = max(sell_prices) if sell_prices else None
        
        # Filtrer par prix si demandé
        if min_price and avg_sell and avg_sell < min_price:
            continue
        if max_price and avg_sell and avg_sell > max_price:
            continue
        
        # Trouver les meilleurs emplacements
        best_buy = min(prices, key=lambda p: p.buy_price or float('inf')) if buy_prices else None
        best_sell = max(prices, key=lambda p: p.sell_price or 0) if sell_prices else None
        
        result.append(MaterialMarketInfo(
            id=material.id,
            name=material.name,
            category=material.category,
            unit=material.unit,
            is_mineable=material.is_mineable,
            is_salvage=material.is_salvage,
            is_trade_good=material.is_trade_good,
            avg_buy_price=avg_buy,
            avg_sell_price=avg_sell,
            min_buy_price=min_buy,
            max_sell_price=max_sell,
            best_buy_location=LocationInfo(
                id=best_buy.location_obj.id,
                name=best_buy.location_obj.name,
                code=best_buy.location_obj.code,
                system=best_buy.location_obj.system,
                planet=best_buy.location_obj.planet,
                location_type=best_buy.location_obj.location_type,
                full_path=best_buy.location_obj.full_location_path,
            ) if best_buy else None,
            best_sell_location=LocationInfo(
                id=best_sell.location_obj.id if best_sell.location_obj else None,
                name=best_sell.location_obj.name if best_sell.location_obj else (best_sell.location_string or "UEX Estimated"),
                code=best_sell.location_obj.code if best_sell.location_obj else "UEX",
                system=best_sell.location_obj.system if best_sell.location_obj else "Unknown",
                planet=best_sell.location_obj.planet if best_sell.location_obj else None,
                location_type=best_sell.location_obj.location_type if best_sell.location_obj else "Estimated",
                full_path=best_sell.location_obj.full_location_path if best_sell.location_obj else "UEX Estimated Price",
            ) if best_sell else None,
            available_at=len(prices),
        ))
    
    return result


@router.get("/materials/{material_id}", response_model=MaterialDetailedMarket)
def get_material_prices(
    material_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les prix détaillés d'un matériau sur toutes les locations.
    
    Retourne la liste complète des prix d'achat et de vente à chaque location
    où le matériau est disponible.
    """
    # Récupérer le matériau
    material = db.query(Material).filter(Material.id == material_id).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Récupérer tous les prix
    prices = db.query(MarketPrice).filter(
        MarketPrice.material_id == material_id
    ).options(
        joinedload(MarketPrice.location_obj)
    ).all()
    
    # Calculer les stats
    buy_prices = [p.buy_price for p in prices if p.buy_price]
    sell_prices = [p.sell_price for p in prices if p.sell_price]
    
    avg_buy = sum(buy_prices) / len(buy_prices) if buy_prices else None
    avg_sell = sum(sell_prices) / len(sell_prices) if sell_prices else None
    min_buy = min(buy_prices) if buy_prices else None
    max_sell = max(sell_prices) if sell_prices else None
    
    best_buy = min(prices, key=lambda p: p.buy_price or float('inf')) if buy_prices else None
    best_sell = max(prices, key=lambda p: p.sell_price or 0) if sell_prices else None
    
    # Construire la réponse
    material_info = MaterialMarketInfo(
        id=material.id,
        name=material.name,
        category=material.category,
        unit=material.unit,
        is_mineable=material.is_mineable,
        is_salvage=material.is_salvage,
        is_trade_good=material.is_trade_good,
        avg_buy_price=avg_buy,
        avg_sell_price=avg_sell,
        min_buy_price=min_buy,
        max_sell_price=max_sell,
        best_buy_location=LocationInfo(
            id=best_buy.location_obj.id,
            name=best_buy.location_obj.name,
            code=best_buy.location_obj.code,
            system=best_buy.location_obj.system,
            planet=best_buy.location_obj.planet,
            location_type=best_buy.location_obj.location_type,
            full_path=best_buy.location_obj.full_location_path,
        ) if best_buy else None,
            best_sell_location=LocationInfo(
                id=best_sell.location_obj.id if best_sell.location_obj else None,
                name=best_sell.location_obj.name if best_sell.location_obj else (best_sell.location_string or "UEX Estimated"),
                code=best_sell.location_obj.code if best_sell.location_obj else "UEX",
                system=best_sell.location_obj.system if best_sell.location_obj else "Unknown",
                planet=best_sell.location_obj.planet if best_sell.location_obj else None,
                location_type=best_sell.location_obj.location_type if best_sell.location_obj else "Estimated",
                full_path=best_sell.location_obj.full_location_path if best_sell.location_obj else "UEX Estimated Price",
            ) if best_sell else None,
            available_at=len(prices),
        )
    
    price_list = [
        PriceInfo(
            location=LocationInfo(
                id=p.location_obj.id,
                name=p.location_obj.name,
                code=p.location_obj.code,
                system=p.location_obj.system,
                planet=p.location_obj.planet,
                location_type=p.location_obj.location_type,
                full_path=p.location_obj.full_location_path,
            ),
            buy_price=p.buy_price,
            sell_price=p.sell_price,
            updated_at=p.updated_at,
        )
        for p in prices
    ]
    
    return MaterialDetailedMarket(
        material=material_info,
        prices=price_list,
    )


@router.get("/trade-routes", response_model=List[TradeRoute])
def get_best_trade_routes(
    min_profit: float = Query(0, description="Minimum profit per unit"),
    limit: int = Query(20, description="Maximum number of routes to return"),
    db: Session = Depends(get_db)
):
    """
    Trouve les meilleures routes commerciales.
    
    Compare les prix d'achat et de vente de tous les matériaux sur toutes les
    locations pour identifier les routes les plus profitables.
    """
    # Récupérer tous les prix avec leurs relations
    all_prices = db.query(MarketPrice).options(
        joinedload(MarketPrice.material),
        joinedload(MarketPrice.location_obj)
    ).all()
    
    # Grouper par matériau
    prices_by_material = {}
    for price in all_prices:
        mat_id = price.material_id
        if mat_id not in prices_by_material:
            prices_by_material[mat_id] = []
        prices_by_material[mat_id].append(price)
    
    routes = []
    
    # Pour chaque matériau, trouver la meilleure route
    for material_id, prices in prices_by_material.items():
        # Trouver le meilleur prix d'achat (le plus bas)
        buy_prices = [p for p in prices if p.buy_price]
        sell_prices = [p for p in prices if p.sell_price]
        
        if not buy_prices or not sell_prices:
            continue
        
        best_buy = min(buy_prices, key=lambda p: p.buy_price)
        best_sell = max(sell_prices, key=lambda p: p.sell_price)
        
        profit = best_sell.sell_price - best_buy.buy_price
        
        if profit < min_profit:
            continue
        
        profit_margin = (profit / best_buy.buy_price) * 100 if best_buy.buy_price > 0 else 0
        
        routes.append(TradeRoute(
            material_name=best_buy.material.name,
            material_id=material_id,
            buy_location=LocationInfo(
                id=best_buy.location_obj.id,
                name=best_buy.location_obj.name,
                code=best_buy.location_obj.code,
                system=best_buy.location_obj.system,
                planet=best_buy.location_obj.planet,
                location_type=best_buy.location_obj.location_type,
                full_path=best_buy.location_obj.full_location_path,
            ),
            buy_price=best_buy.buy_price,
            sell_location=LocationInfo(
                id=best_sell.location_obj.id if best_sell.location_obj else None,
                name=best_sell.location_obj.name if best_sell.location_obj else (best_sell.location_string or "UEX Estimated"),
                code=best_sell.location_obj.code if best_sell.location_obj else "UEX",
                system=best_sell.location_obj.system if best_sell.location_obj else "Unknown",
                planet=best_sell.location_obj.planet if best_sell.location_obj else None,
                location_type=best_sell.location_obj.location_type if best_sell.location_obj else "Estimated",
                full_path=best_sell.location_obj.full_location_path if best_sell.location_obj else "UEX Estimated Price",
            ),
            sell_price=best_sell.sell_price,
            profit_per_unit=profit,
            profit_margin_percent=profit_margin,
        ))
    
    # Trier par profit décroissant
    routes.sort(key=lambda r: r.profit_per_unit, reverse=True)
    
    return routes[:limit]


@router.get("/locations/{location_id}/prices", response_model=List[PriceInfo])
def get_location_prices(
    location_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère tous les prix des matériaux disponibles à une location donnée.
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    prices = db.query(MarketPrice).filter(
        MarketPrice.location_id == location_id
    ).options(
        joinedload(MarketPrice.material),
        joinedload(MarketPrice.location_obj)
    ).all()
    
    return [
        PriceInfo(
            location=LocationInfo(
                id=location.id,
                name=location.name,
                code=location.code,
                system=location.system,
                planet=location.planet,
                location_type=location.location_type,
                full_path=location.full_location_path,
            ),
            buy_price=p.buy_price,
            sell_price=p.sell_price,
            updated_at=p.updated_at,
        )
        for p in prices
    ]