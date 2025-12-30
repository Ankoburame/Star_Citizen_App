"""
Script pour importer automatiquement tous les matériaux depuis UEX dans la DB.
À exécuter une fois pour remplir la table materials.
"""

import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy.orm import Session

from database import SessionLocal
from models.material import Material
from models.market_price import MarketPrice
from core.config import UEX_API_TOKEN

UEX_API_BASE_URL = "https://api.uexcorp.space/2.0"
HEADERS = {
    "Authorization": f"Bearer {UEX_API_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "StarCitizen-App/1.0",
}


def fetch_all_commodities():
    """Récupère toutes les commodities depuis UEX."""
    url = f"{UEX_API_BASE_URL}/commodities"
    
    print("🌐 Fetching commodities from UEX...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: {response.status_code}")
    
    commodities = response.json().get("data", [])
    print(f"✅ Received {len(commodities)} commodities")
    
    return commodities


def categorize_commodity(commodity):
    """
    Détermine la catégorie et les flags d'un matériau.
    
    Returns:
        dict avec category, is_mineable, is_salvage, is_trade_good
    """
    name = commodity.get("name", "").lower()
    code = commodity.get("code", "").lower()
    kind = commodity.get("kind", "").lower()
    
    # Minerais
    if "(ore)" in name or "(raw)" in name or "raw" in name:
        return {
            "category": "mineral",
            "is_mineable": True,
            "is_salvage": False,
            "is_trade_good": False,
        }
    
    # Minerais raffinés (gems)
    mineral_keywords = [
        "agricium", "aluminum", "beryl", "bexalite", "borase", "copper",
        "corundum", "diamond", "gold", "hadanite", "hephaestanite", "iron",
        "laranite", "quantanium", "quartz", "taranite", "titanium", "tungsten",
        "aphorite", "dolivine", "janalite", "bexalite", "laranite",
        "cobalt", "riccite", "silicon", "tin", "saldynium", "jaclium",
        "carinite", "lindinium", "torite", "savrilium"
    ]
    
    if any(kw in name for kw in mineral_keywords):
        return {
            "category": "mineral",
            "is_mineable": True,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Salvage
    salvage_keywords = [
        "scrap", "rmc", "recycled", "construction materials", "rubble",
        "pebbles", "salvage", "waste"
    ]
    
    if any(kw in name for kw in salvage_keywords):
        return {
            "category": "salvage",
            "is_mineable": False,
            "is_salvage": True,
            "is_trade_good": True,
        }
    
    # Gaz
    gas_keywords = [
        "helium", "hydrogen", "neon", "argon", "nitrogen", "chlorine",
        "fluorine", "iodine", "ammonia", "methane", "krypton", "xenon",
        "anti-hydrogen"
    ]
    
    if any(kw in name for kw in gas_keywords) or "gas" in kind:
        return {
            "category": "trade",
            "is_mineable": False,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Drogues
    drug_keywords = [
        "widow", "slam", "maze", "e'tam", "neon", "altruciatoxin",
        "dopple", "freeze", "glow", "mala", "thrust", "zip"
    ]
    
    if any(kw in name for kw in drug_keywords):
        return {
            "category": "trade",
            "is_mineable": False,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Nourriture
    food_keywords = [
        "food", "berries", "root", "egg", "medmon", "pitambu", "prota",
        "dung", "limes", "lunes"
    ]
    
    if any(kw in name for kw in food_keywords):
        return {
            "category": "trade",
            "is_mineable": False,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Médical
    medical_keywords = [
        "medical", "medstick", "stim", "plague"
    ]
    
    if any(kw in name for kw in medical_keywords):
        return {
            "category": "trade",
            "is_mineable": False,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Items événementiels
    if "envelope" in name or "luminalia" in name or "year of" in name:
        return {
            "category": "trade",
            "is_mineable": False,
            "is_salvage": False,
            "is_trade_good": True,
        }
    
    # Par défaut : trade good
    return {
        "category": "trade",
        "is_mineable": False,
        "is_salvage": False,
        "is_trade_good": True,
    }


def import_materials(db: Session, dry_run: bool = False):
    """
    Importe tous les matériaux depuis UEX dans la DB.
    
    Args:
        db: Session database
        dry_run: Si True, affiche seulement ce qui serait importé sans modifier la DB
    """
    commodities = fetch_all_commodities()
    
    # Récupérer les matériaux existants
    existing = {m.name.lower(): m for m in db.query(Material).all()}
    print(f"📦 {len(existing)} matériaux déjà en DB")
    
    stats = {
        "added": 0,
        "skipped": 0,
        "updated": 0,
    }
    
    for commodity in commodities:
        name = commodity.get("name", "").strip()
        
        if not name:
            continue
        
        name_lower = name.lower()
        
        # Vérifier si existe déjà
        if name_lower in existing:
            stats["skipped"] += 1
            continue
        
        # Catégoriser
        props = categorize_commodity(commodity)
        
        if dry_run:
            print(f"  ➕ Would add: {name} ({props['category']})")
            stats["added"] += 1
        else:
            # Créer le matériau
            material = Material(
                name=name,
                category=props["category"],
                unit="SCU",
                is_mineable=props["is_mineable"],
                is_salvage=props["is_salvage"],
                is_trade_good=props["is_trade_good"],
                sell_price=None,  # Sera rempli par le refresh des prix
            )
            
            db.add(material)
            stats["added"] += 1
            print(f"✅ Added: {name} ({props['category']})")
    
    if not dry_run:
        db.commit()
        print(f"\n🎉 Import complete!")
    else:
        print(f"\n📊 Dry run complete (no changes made)")
    
    print(f"   Added: {stats['added']}")
    print(f"   Skipped (already exists): {stats['skipped']}")


def main():
    """Point d'entrée du script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import materials from UEX")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without making changes"
    )
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("UEX MATERIALS IMPORT")
        print("=" * 60)
        
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made")
            print()
        
        import_materials(db, dry_run=args.dry_run)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()