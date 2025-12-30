"""
Script pour rafraîchir les prix des matériaux sur tous les marchés depuis UEX.
Récupère les prix d'achat et de vente pour chaque matériau à chaque location.

Ce script devrait être exécuté régulièrement (cron job) pour maintenir les prix à jour.

Usage:
    python scripts/refresh_market_prices.py                    # Refresh complet
    python scripts/refresh_market_prices.py --dry-run         # Test sans modification
    python scripts/refresh_market_prices.py --material Gold   # Refresh un seul matériau
    python scripts/refresh_market_prices.py --clean-old       # Supprime les vieux prix (>7j)
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


def fetch_commodity_prices(commodity_code: str) -> List[Dict[str, Any]]:
    """
    Récupère les prix d'un matériau sur tous les terminaux depuis UEX.
    
    Args:
        commodity_code: Code UEX du matériau (ex: "gold", "quantanium")
        
    Returns:
        Liste des prix par terminal
        
    Raises:
        RuntimeError: Si l'API UEX retourne une erreur
    """
    url = f"{UEX_API_BASE_URL}/commodities/{commodity_code}/prices"
    
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code == 404:
        # Matériau non trouvé dans UEX
        return []
    
    if response.status_code != 200:
        raise RuntimeError(
            f"UEX API error for {commodity_code}: {response.status_code}"
        )
    
    prices = response.json().get("data", [])
    return prices


def fetch_all_prices() -> Dict[str, List[Dict[str, Any]]]:
    """
    Récupère tous les prix de tous les matériaux depuis UEX.
    
    UEX ne fournit pas d'endpoint global pour tous les prix,
    donc on récupère les prix matériau par matériau.
    
    Returns:
        Dictionnaire {material_code: [prices]}
    """
    # D'abord, récupérer la liste de tous les commodities
    url = f"{UEX_API_BASE_URL}/commodities"
    
    print("🌐 Fetching commodities list from UEX...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: {response.status_code}")
    
    commodities = response.json().get("data", [])
    print(f"✅ Found {len(commodities)} commodities")
    
    # Maintenant, récupérer les prix pour chaque commodity
    print("🌐 Fetching prices for each commodity...")
    prices_by_material = {}
    errors = 0
    
    for i, commodity in enumerate(commodities, 1):
        commodity_code = commodity.get("code", "").lower()
        if not commodity_code:
            continue
        
        # Afficher la progression tous les 20 matériaux
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(commodities)} commodities processed...")
        
        try:
            # Récupérer les prix pour ce commodity
            price_url = f"{UEX_API_BASE_URL}/commodities/{commodity_code}/prices"
            price_response = requests.get(price_url, headers=HEADERS, timeout=10)
            
            if price_response.status_code == 404:
                # Commodity sans prix, pas grave
                continue
            
            if price_response.status_code != 200:
                errors += 1
                continue
            
            prices = price_response.json().get("data", [])
            if prices:
                prices_by_material[commodity_code] = prices
                
        except requests.exceptions.Timeout:
            errors += 1
            continue
        except Exception as e:
            errors += 1
            continue
    
    print(f"✅ Received prices for {len(prices_by_material)} commodities")
    if errors > 0:
        print(f"⚠️  {errors} errors occurred while fetching prices")
    
    return prices_by_material


def normalize_material_name(uex_name: str) -> str:
    """
    Normalise le nom d'un matériau UEX pour matcher avec notre DB.
    
    Args:
        uex_name: Nom depuis UEX
        
    Returns:
        Nom normalisé
    """
    # Supprimer les suffixes communs
    name = uex_name.replace(" (Ore)", "").replace(" (Raw)", "")
    name = name.replace(" - Refined", "").strip()
    
    return name


def update_market_prices(
    db: Session,
    dry_run: bool = False,
    specific_material: Optional[str] = None
) -> Dict[str, int]:
    """
    Met à jour les prix du market depuis UEX.
    
    Args:
        db: Session SQLAlchemy
        dry_run: Si True, affiche ce qui serait fait sans modifier la DB
        specific_material: Si spécifié, ne met à jour que ce matériau
        
    Returns:
        Statistiques d'import
    """
    # Charger tous les matériaux et locations de la DB
    materials = {m.name.lower(): m for m in db.query(Material).all()}
    locations = {loc.code.lower(): loc for loc in db.query(Location).all()}
    
    print(f"📦 {len(materials)} materials in DB")
    print(f"📦 {len(locations)} locations in DB")
    
    stats = {
        "added": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    # Récupérer les prix depuis UEX
    if specific_material:
        # Mode single material
        print(f"\n🔍 Fetching prices for {specific_material}...")
        material_lower = specific_material.lower()
        
        if material_lower not in materials:
            print(f"❌ Material '{specific_material}' not found in DB")
            return stats
        
        material = materials[material_lower]
        prices_data = {material_lower: fetch_commodity_prices(material_lower)}
    else:
        # Mode all materials
        prices_data = fetch_all_prices()
    
    # Traiter chaque matériau
    for material_code, price_entries in prices_data.items():
        material_name = normalize_material_name(material_code)
        material_lower = material_name.lower()
        
        # Trouver le matériau dans notre DB
        if material_lower not in materials:
            # Essayer avec le code directement
            if material_code not in materials:
                stats["skipped"] += 1
                continue
            material = materials[material_code]
        else:
            material = materials[material_lower]
        
        # Traiter chaque prix
        for price_entry in price_entries:
            try:
                terminal_code = price_entry.get("terminal_code", "").lower()
                
                if not terminal_code or terminal_code not in locations:
                    stats["skipped"] += 1
                    continue
                
                location = locations[terminal_code]
                
                buy_price = price_entry.get("price_buy")
                sell_price = price_entry.get("price_sell")
                
                # Vérifier si un prix existe déjà
                existing_price = db.query(MarketPrice).filter(
                    and_(
                        MarketPrice.material_id == material.id,
                        MarketPrice.location_id == location.id
                    )
                ).first()
                
                if existing_price:
                    # Mettre à jour
                    if dry_run:
                        print(f"  🔄 Would update: {material.name} @ {location.name}")
                        stats["updated"] += 1
                    else:
                        existing_price.buy_price = buy_price
                        existing_price.sell_price = sell_price
                        existing_price.source = "UEX"
                        existing_price.updated_at = datetime.utcnow()
                        stats["updated"] += 1
                else:
                    # Créer nouveau
                    if dry_run:
                        print(f"  ➕ Would add: {material.name} @ {location.name}")
                        stats["added"] += 1
                    else:
                        new_price = MarketPrice(
                            material_id=material.id,
                            location_id=location.id,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            source="UEX",
                        )
                        db.add(new_price)
                        stats["added"] += 1
            
            except Exception as e:
                print(f"❌ Error processing price entry: {e}")
                stats["errors"] += 1
    
    if not dry_run:
        try:
            db.commit()
            print(f"\n🎉 Market prices updated!")
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
        description="Refresh market prices from UEX API"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--material",
        type=str,
        help="Only refresh prices for this specific material"
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
        print("MARKET PRICES REFRESH")
        print("=" * 60)
        
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made")
        
        print()
        
        if args.clean_old:
            clean_old_prices(db, days=args.days, dry_run=args.dry_run)
        else:
            stats = update_market_prices(
                db,
                dry_run=args.dry_run,
                specific_material=args.material
            )
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