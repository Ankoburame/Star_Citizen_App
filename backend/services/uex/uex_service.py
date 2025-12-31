"""
Service UEX générique pour récupérer tous les prix des commodities.
Remplace quantanium_service.py avec une approche plus large.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from core.config import UEX_API_TOKEN
from models.market_price import MarketPrice
from models.material import Material

# Configuration
UEX_API_BASE_URL = "https://api.uexcorp.space/2.0"
UEX_LOCATION = "UEX_ESTIMATED"
CACHE_TTL_HOURS = 12

HEADERS = {
    "Authorization": f"Bearer {UEX_API_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "StarCitizen-App/1.0",
}


def is_cache_valid(db: Session, material_id: Optional[int] = None) -> bool:
    """
    Vérifie si le cache des prix UEX est encore valide.
    
    Args:
        db: Session de base de données
        material_id: ID du matériau spécifique (None = vérification globale)
        
    Returns:
        True si le cache est valide, False sinon
    """
    cache_threshold = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)
    
    query = db.query(MarketPrice).filter(
        MarketPrice.source == "UEX",
        MarketPrice.location == UEX_LOCATION,
    )
    
    if material_id:
        query = query.filter(MarketPrice.material_id == material_id)
    
    latest = query.order_by(desc(MarketPrice.collected_at)).first()
    
    if not latest:
        return False
    
    return latest.collected_at >= cache_threshold


def fetch_all_commodities_from_uex() -> List[Dict]:
    """
    Récupère toutes les commodities depuis l'API UEX.
    
    Returns:
        Liste de dictionnaires contenant les données des commodities
        
    Raises:
        RuntimeError: Si l'appel API échoue
    """
    url = f"{UEX_API_BASE_URL}/commodities"
    
    print(f"🌐 Fetching all commodities from UEX API...")
    
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: HTTP {response.status_code}")
    
    payload = response.json()
    commodities = payload.get("data", [])
    
    print(f"✅ Received {len(commodities)} commodities from UEX")
    
    return commodities


def fetch_commodity_prices(commodity_id: int) -> List[Dict]:
    """
    Récupère les prix d'une commodity spécifique pour toutes les locations.
    
    Args:
        commodity_id: ID de la commodity sur UEX
        
    Returns:
        Liste des prix par location
        
    Raises:
        RuntimeError: Si l'appel API échoue
    """
    url = f"{UEX_API_BASE_URL}/commodities/{commodity_id}/prices"
    
    response = requests.get(url, headers=HEADERS, timeout=15)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error for commodity {commodity_id}: HTTP {response.status_code}")
    
    payload = response.json()
    return payload.get("data", [])


def map_uex_commodity_to_material(
    db: Session,
    uex_commodity: Dict
) -> Optional[Material]:
    """
    Trouve le matériau correspondant dans la DB à partir d'une commodity UEX.
    
    Essaie de matcher par nom (insensible à la casse).
    
    Args:
        db: Session de base de données
        uex_commodity: Dictionnaire de commodity UEX
        
    Returns:
        Objet Material correspondant ou None si non trouvé
    """
    uex_name = uex_commodity.get("name", "").strip()
    uex_code = uex_commodity.get("code", "").strip()
    
    if not uex_name:
        return None
    
    # Recherche par nom (case insensitive)
    material = db.query(Material).filter(
        Material.name.ilike(uex_name)
    ).first()
    
    if material:
        return material
    
    # Recherche par code si disponible
    if uex_code:
        material = db.query(Material).filter(
            Material.name.ilike(f"%{uex_code}%")
        ).first()
    
    return material


def refresh_all_prices(db: Session, force: bool = False) -> Dict[str, int]:
    """
    Rafraîchit les prix de tous les matériaux depuis UEX.
    
    Args:
        db: Session de base de données
        force: Si True, ignore le cache et force le refresh
        
    Returns:
        Dictionnaire avec statistiques (updated, skipped, errors)
    """
    if not force and is_cache_valid(db):
        print("⏭️  Cache still valid, skipping refresh")
        return {"updated": 0, "skipped": 0, "errors": 0, "message": "Cache valid"}
    
    print("🔄 Starting full price refresh...")
    
    stats = {
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    try:
        # Récupérer toutes les commodities
        commodities = fetch_all_commodities_from_uex()
        
        for commodity in commodities:
            try:
                # Trouver le matériau correspondant
                material = map_uex_commodity_to_material(db, commodity)
                
                material = map_uex_commodity_to_material(db, commodity)

                if not material:
                    # CRÉER le matériau s'il n'existe pas
                    uex_name = commodity.get('name', '').strip()
                    if uex_name:
                        material = Material(
                            name=uex_name,
                            category=commodity.get('type', 'Commodity'),
                            is_trade_good=True
                        )
                        db.add(material)
                        db.flush()  # Pour avoir l'ID
                        print(f"✨ Created new material: {material.name}")
                    else:
                        stats["skipped"] += 1
                        continue
                
                # Récupérer le meilleur prix de vente
                commodity_id = commodity.get("id")
                sell_price = commodity.get("price_sell")
                
                if not sell_price or sell_price <= 0:
                    print(f"⚠️  No valid sell price for {material.name}")
                    stats["skipped"] += 1
                    continue
                
                # Créer ou mettre à jour le prix
                now = datetime.utcnow()
                
                market_price = MarketPrice(
                    material_id=material.id,
                    location=UEX_LOCATION,
                    sell_price=sell_price,
                    buy_price=commodity.get("price_buy"),
                    source="UEX",
                    updated_at=now,
                    collected_at=now,
                )
                
                db.add(market_price)
                stats["updated"] += 1
                
                print(f"✅ Updated {material.name}: {sell_price:,.2f} aUEC")
                
            except Exception as e:
                print(f"❌ Error processing commodity {commodity.get('name', 'Unknown')}: {e}")
                stats["errors"] += 1
                continue
        
        db.commit()
        print(f"🎉 Refresh complete! Updated: {stats['updated']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error during refresh: {e}")
        raise
    
    return stats


def refresh_single_material(
    db: Session,
    material_id: int,
    force: bool = False
) -> bool:
    """
    Rafraîchit le prix d'un seul matériau.
    
    Args:
        db: Session de base de données
        material_id: ID du matériau à rafraîchir
        force: Si True, ignore le cache
        
    Returns:
        True si mis à jour avec succès, False sinon
    """
    if not force and is_cache_valid(db, material_id):
        print(f"⏭️  Cache valid for material {material_id}")
        return False
    
    material = db.query(Material).filter(Material.id == material_id).first()
    
    if not material:
        raise ValueError(f"Material {material_id} not found")
    
    print(f"🔄 Refreshing price for {material.name}...")
    
    try:
        # Récupérer toutes les commodities pour trouver celle qui correspond
        commodities = fetch_all_commodities_from_uex()
        
        for commodity in commodities:
            if commodity.get("name", "").lower() == material.name.lower():
                sell_price = commodity.get("price_sell")
                
                if not sell_price or sell_price <= 0:
                    print(f"⚠️  No valid sell price for {material.name}")
                    return False
                
                now = datetime.utcnow()
                
                market_price = MarketPrice(
                    material_id=material.id,
                    location=UEX_LOCATION,
                    sell_price=sell_price,
                    buy_price=commodity.get("price_buy"),
                    source="UEX",
                    updated_at=now,
                    collected_at=now,
                )
                
                db.add(market_price)
                db.commit()
                
                print(f"✅ Updated {material.name}: {sell_price:,.2f} aUEC")
                return True
        
        print(f"⚠️  No UEX commodity found for {material.name}")
        return False
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error refreshing {material.name}: {e}")
        raise


def get_material_price_history(
    db: Session,
    material_id: int,
    days: int = 30
) -> List[MarketPrice]:
    """
    Récupère l'historique des prix d'un matériau.
    
    Args:
        db: Session de base de données
        material_id: ID du matériau
        days: Nombre de jours d'historique
        
    Returns:
        Liste des prix historiques
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    return (
        db.query(MarketPrice)
        .filter(
            MarketPrice.material_id == material_id,
            MarketPrice.source == "UEX",
            MarketPrice.collected_at >= since
        )
        .order_by(MarketPrice.collected_at.desc())
        .all()
    )