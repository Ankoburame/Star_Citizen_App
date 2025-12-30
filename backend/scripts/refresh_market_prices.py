"""
Script pour rafraîchir les prix moyens depuis UEX API v2.0.
Stocke les prix moyens globaux dans une location virtuelle "UEX_AVG".

L'API UEX v2.0 ne fournit plus de prix par terminal individuel,
seulement des moyennes globales par commodity.

Usage:
    python scripts/refresh_market_prices.py                    # Refresh complet
    python scripts/refresh_market_prices.py --dry-run         # Test sans modification
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Ajouter le dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import SessionLocal
from models.material import Material
from models.location import Location
from models.market_price import MarketPrice
from core.config import UEX_API_TOKEN

UEX_API_BASE_URL = "https://api.uexcorp.space/2.0"
HEADERS = {
    "Authorization": f"Bearer {UEX_API_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "StarCitizen-App/1.0",
}


def fetch_all_commodities() -> List[Dict[str, Any]]:
    """
    Récupère tous les commodities avec leurs prix moyens depuis UEX.
    
    Returns:
        Liste des commodities avec prix moyens
        
    Raises:
        RuntimeError: Si l'API UEX retourne une erreur
    """
    url = f"{UEX_API_BASE_URL}/commodities"
    
    print("🌐 Fetching commodities with average prices from UEX...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: {response.status_code}")
    
    commodities = response.json().get("data", [])
    print(f"✅ Found {len(commodities)} commodities with average prices")
    
    return commodities


def find_material_in_db(uex_code: str, uex_name: str, materials_dict: Dict) -> Optional[Material]:
    """
    Trouve un matériau dans la DB en utilisant plusieurs stratégies de matching.
    
    Args:
        uex_code: Code depuis UEX (ex: "AGRI")
        uex_name: Nom depuis UEX (ex: "Agricium")
        materials_dict: Dictionnaire des matériaux {name_lower: material}
        
    Returns:
        Material trouvé ou None
    """
    # Stratégie 1: Match exact par nom
    if uex_name.lower() in materials_dict:
        return materials_dict[uex_name.lower()]
    
    # Stratégie 2: Match partiel (enlever suffixes comme "(Ore)")
    clean_name = uex_name.replace(" (Ore)", "").replace(" (Raw)", "").replace(" - Refined", "").strip()
    if clean_name.lower() in materials_dict:
        return materials_dict[clean_name.lower()]
    
    # Stratégie 3: Fuzzy match
    for db_name, material in materials_dict.items():
        if db_name in uex_name.lower() or uex_name.lower() in db_name:
            return material
    
    return None


def update_market_prices(
    db: Session,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Met à jour les prix moyens depuis UEX dans la location virtuelle UEX_AVG.
    
    Args:
        db: Session SQLAlchemy
        dry_run: Si True, affiche ce qui serait fait sans modifier la DB
        
    Returns:
        Statistiques d'import
    """
    # Charger tous les matériaux
    materials = {m.name.lower(): m for m in db.query(Material).all()}
    
    # Trouver la location virtuelle UEX_AVG
    uex_avg_location = db.query(Location).filter(Location.code == "UEX_AVG").first()
    
    if not uex_avg_location:
        print("❌ Location UEX_AVG not found in DB!")
        print("Please run the migration: migration_uex_avg_location.sql")
        return {"added": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    print(f"📦 {len(materials)} materials in DB")
    print(f"📍 Using location: {uex_avg_location.name} (ID: {uex_avg_location.id})")
    
    stats = {
        "added": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    # Récupérer les commodities depuis UEX
    commodities = fetch_all_commodities()
    
    materials_matched = 0
    materials_not_found = 0
    
    print("\n🔄 Processing commodities...")
    
    # Traiter chaque commodity
    for i, commodity in enumerate(commodities, 1):
        try:
            uex_code = commodity.get("code", "")
            uex_name = commodity.get("name", "")
            price_buy = commodity.get("price_buy")
            price_sell = commodity.get("price_sell")
            
            # Afficher progression
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(commodities)} commodities processed...")
            
            # Skip si pas de prix
            if not price_buy and not price_sell:
                stats["skipped"] += 1
                continue
            
            # Trouver le matériau dans notre DB
            material = find_material_in_db(uex_code, uex_name, materials)
            
            if not material:
                materials_not_found += 1
                stats["skipped"] += 1
                continue
            
            materials_matched += 1
            
            # Vérifier si un prix existe déjà pour ce matériau dans UEX_AVG
            existing_price = db.query(MarketPrice).filter(
                and_(
                    MarketPrice.material_id == material.id,
                    MarketPrice.location_id == uex_avg_location.id
                )
            ).first()
            
            if existing_price:
                # Mettre à jour seulement si les prix ont changé
                if (existing_price.buy_price != price_buy or 
                    existing_price.sell_price != price_sell):
                    if dry_run:
                        print(f"  🔄 Would update: {material.name} (buy: {price_buy}, sell: {price_sell})")
                        stats["updated"] += 1
                    else:
                        existing_price.buy_price = price_buy
                        existing_price.sell_price = price_sell
                        existing_price.source = "UEX_AVG"
                        existing_price.updated_at = datetime.utcnow()
                        stats["updated"] += 1
                else:
                    stats["skipped"] += 1
            else:
                # Créer nouveau prix moyen
                if dry_run:
                    print(f"  ➕ Would add: {material.name} (buy: {price_buy}, sell: {price_sell})")
                    stats["added"] += 1
                else:
                    new_price = MarketPrice(
                        material_id=material.id,
                        location_id=uex_avg_location.id,
                        buy_price=price_buy,
                        sell_price=price_sell,
                        source="UEX_AVG",
                    )
                    db.add(new_price)
                    stats["added"] += 1
        
        except Exception as e:
            print(f"❌ Error processing commodity {commodity.get('name', 'unknown')}: {e}")
            stats["errors"] += 1
    
    print(f"\n📊 Materials matched: {materials_matched}/{len(commodities)}")
    print(f"📊 Materials not found in DB: {materials_not_found}")
    
    if not dry_run:
        try:
            db.commit()
            print(f"\n🎉 Market average prices updated!")
        except Exception as e:
            db.rollback()
            print(f"\n❌ Commit failed: {e}")
            raise
    else:
        print(f"\n📊 Dry run complete (no changes made)")
    
    return stats


def clean_old_prices(db: Session, days: int = 7, dry_run: bool = False) -> int:
    """
    Supprime les prix obsolètes (non mis à jour depuis X jours).
    
    Args:
        db: Session SQLAlchemy
        days: Nombre de jours avant qu'un prix soit considéré obsolète
        dry_run: Si True, affiche ce qui serait supprimé sans le faire
        
    Returns:
        Nombre de prix supprimés
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    old_prices = db.query(MarketPrice).filter(
        MarketPrice.updated_at < cutoff_date
    ).all()
    
    count = len(old_prices)
    
    if dry_run:
        print(f"📊 Would delete {count} prices older than {days} days")
    else:
        for price in old_prices:
            db.delete(price)
        db.commit()
        print(f"🗑️  Deleted {count} old prices")
    
    return count


def print_stats(stats: Dict[str, int]):
    """Affiche les statistiques de refresh."""
    print("\n" + "=" * 60)
    print("REFRESH STATISTICS")
    print("=" * 60)
    print(f"  ✅ Added:     {stats['added']}")
    print(f"  🔄 Updated:   {stats['updated']}")
    print(f"  ⏭️  Skipped:   {stats['skipped']}")
    print(f"  ❌ Errors:    {stats['errors']}")
    print(f"  📊 Total:     {sum(stats.values())}")
    print("=" * 60)


def main():
    """Point d'entrée principal du script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Refresh average market prices from UEX API v2.0"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--clean-old",
        action="store_true",
        help="Remove prices older than 7 days"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days threshold for --clean-old (default: 7)"
    )
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("MARKET AVERAGE PRICES REFRESH (UEX v2.0)")
        print("=" * 60)
        
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made")
        
        print()
        
        if args.clean_old:
            clean_old_prices(db, days=args.days, dry_run=args.dry_run)
        else:
            stats = update_market_prices(db, dry_run=args.dry_run)
            print_stats(stats)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        print("Please check your internet connection and UEX API token.")
        db.rollback()
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        db.rollback()
        raise
        
    finally:
        db.close()


if __name__ == "__main__":
    main()