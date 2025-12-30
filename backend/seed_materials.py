"""
Seed script pour importer les matériaux dans la base de données.
Gère les minéraux, le salvage et les biens commerciaux de Star Citizen.
"""

import logging
from typing import List, Tuple
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models.material import Material

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type alias pour plus de clarté
MaterialData = Tuple[str, str, str, bool, bool, bool]

# Liste des matériaux à importer
# Format: (nom, catégorie, unité, minable, salvage, commerce)
MATERIALS: List[MaterialData] = [
    # Minéraux minables
    ("Stileron", "mineral", "SCU", True, False, False),
    ("Quantanium", "mineral", "SCU", True, False, False),
    ("Riccite", "mineral", "SCU", True, False, False),
    ("Salvrilium", "mineral", "SCU", True, False, False),
    ("Taranite", "mineral", "SCU", True, False, True),
    ("Lindinium", "mineral", "SCU", True, False, False),
    ("Bexalite", "mineral", "SCU", True, False, True),
    ("Gold", "mineral", "SCU", True, False, True),
    ("Borase", "mineral", "SCU", True, False, False),
    ("Laranite", "mineral", "SCU", True, False, True),
    ("Beryl", "mineral", "SCU", True, False, True),
    ("Agricium", "mineral", "SCU", True, False, True),
    ("Hephaestanite", "mineral", "SCU", True, False, True),
    ("Ice", "mineral", "SCU", True, False, False),
    ("Tungsten", "mineral", "SCU", True, False, True),
    ("Titanium", "mineral", "SCU", True, False, True),
    ("Iron", "mineral", "SCU", True, False, True),
    ("Quartz", "mineral", "SCU", True, False, True),
    ("Torite", "mineral", "SCU", True, False, False),
    ("Corundum", "mineral", "SCU", True, False, True),
    ("Copper", "mineral", "SCU", True, False, True),
    ("Tin", "mineral", "SCU", True, False, True),
    ("Aluminium", "mineral", "SCU", True, False, True),
    ("Silicon", "mineral", "SCU", True, False, True),
    ("Inert Material", "mineral", "SCU", True, False, False),
    ("Janalite", "mineral", "SCU", True, False, True),
    ("Hadanite", "mineral", "SCU", True, False, False),
    ("Feynmaline", "mineral", "SCU", True, False, False),
    ("Aphorite", "mineral", "SCU", True, False, False),
    ("Dolivine", "mineral", "SCU", True, False, False),
    ("Glascosite", "mineral", "SCU", True, False, False),
    ("Carinite", "mineral", "SCU", True, False, False),
    ("Jaclium", "mineral", "SCU", True, False, False),
    ("Saldynium", "mineral", "SCU", True, False, False),

    # Matériaux de salvage
    ("RMC", "salvage", "SCU", False, True, True),
    ("Scrap", "salvage", "SCU", False, True, True),
    ("Construction Materials", "salvage", "SCU", False, True, True),

    # Biens commerciaux
    ("Agricultural Supplies", "trade", "SCU", False, False, True),
    ("Ammonia", "trade", "SCU", False, False, True),
    ("Argon", "trade", "SCU", False, False, True),
    ("Astanite", "trade", "SCU", False, False, True),
    ("Atlasium", "trade", "SCU", False, False, True),
    ("Audio Visual Equipment", "trade", "SCU", False, False, True),
    ("Beradum", "trade", "SCU", False, False, True),
    ("Bioplastic", "trade", "SCU", False, False, True),
    ("Carbon", "trade", "SCU", False, False, True),
    ("Carbon-Silk", "trade", "SCU", False, False, True),
    ("Chlorine", "trade", "SCU", False, False, True),
    ("Cobalt", "trade", "SCU", False, False, True),
    ("Compboard", "trade", "SCU", False, False, True),
    ("Degnous Root", "trade", "SCU", False, False, True),
    ("Diamond", "trade", "SCU", False, False, True),
    ("Diamond Laminate", "trade", "SCU", False, False, True),
    ("Distilled Spirits", "trade", "SCU", False, False, True),
    ("Dymantium", "trade", "SCU", False, False, True),
    ("DynaFlex", "trade", "SCU", False, False, True),
    ("Fluorine", "trade", "SCU", False, False, True),
    ("Fresh Food", "trade", "SCU", False, False, True),
    ("Golden Medmon", "trade", "SCU", False, False, True),
    ("Heart of the Woods", "trade", "SCU", False, False, True),
    ("Helium", "trade", "SCU", False, False, True),
    ("Hydrogen", "trade", "SCU", False, False, True),
    ("Iodine", "trade", "SCU", False, False, True),
    ("Kopion Horn", "trade", "SCU", False, False, True),
    ("Luminalia Gift", "trade", "SCU", False, False, True),
    ("Marok Gem", "trade", "SCU", False, False, True),
    ("Medical Supplies", "trade", "SCU", False, False, True),
    ("Mercury", "trade", "SCU", False, False, True),
    ("Methane", "trade", "SCU", False, False, True),
    ("Nitrogen", "trade", "SCU", False, False, True),
    ("Omnapoxy", "trade", "SCU", False, False, True),
    ("Party Favors", "trade", "SCU", False, False, True),
    ("Potassium", "trade", "SCU", False, False, True),
    ("Pressurized Ice", "trade", "SCU", False, False, True),
    ("Processed Food", "trade", "SCU", False, False, True),
    ("Prota", "trade", "SCU", False, False, True),
    ("Ranta Dung", "trade", "SCU", False, False, True),
    ("Revenant Tree Pollen", "trade", "SCU", False, False, True),
    ("Ship Ammunition", "trade", "SCU", False, False, True),
    ("Souvenirs", "trade", "SCU", False, False, True),
    ("Steel", "trade", "SCU", False, False, True),
    ("Stims", "trade", "SCU", False, False, True),
    ("Sunset Berries", "trade", "SCU", False, False, True),
    ("Thermalfoam", "trade", "SCU", False, False, True),
    ("Waste", "trade", "SCU", False, False, True),
    ("Xa'Pyen", "trade", "SCU", False, False, True),
    ("Year Of The Pig Envelope", "trade", "SCU", False, False, True),
]


def seed_materials() -> None:
    """
    Importe les matériaux dans la base de données.
    
    Cette fonction:
    - Vérifie si chaque matériau existe déjà
    - N'insère que les nouveaux matériaux
    - Gère les erreurs de base de données
    - Affiche un rapport détaillé
    
    Raises:
        SQLAlchemyError: En cas d'erreur de base de données
    """
    db = SessionLocal()
    added_count = 0
    skipped_count = 0
    
    try:
        logger.info("Début de l'import des matériaux...")
        
        for name, category, unit, is_mineable, is_salvage, is_trade_good in MATERIALS:
            # Vérifier si le matériau existe déjà
            existing_material = db.query(Material).filter_by(name=name).first()
            
            if existing_material:
                logger.debug(f"Matériau déjà existant: {name}")
                skipped_count += 1
                continue
            
            # Créer et ajouter le nouveau matériau
            new_material = Material(
                name=name,
                category=category,
                unit=unit,
                is_mineable=is_mineable,
                is_salvage=is_salvage,
                is_trade_good=is_trade_good
            )
            db.add(new_material)
            logger.debug(f"Matériau ajouté: {name} ({category})")
            added_count += 1
        
        # Commit une seule fois à la fin
        db.commit()
        
        # Rapport final
        logger.info("=" * 50)
        logger.info("Rapport d'import des matériaux:")
        logger.info(f"  ✅ Matériaux ajoutés: {added_count}")
        logger.info(f"  ⏭️  Matériaux existants ignorés: {skipped_count}")
        logger.info(f"  📊 Total traité: {len(MATERIALS)}")
        logger.info("=" * 50)
        
        if added_count > 0:
            logger.info("✅ Import des matériaux terminé avec succès!")
        else:
            logger.info("ℹ️  Aucun nouveau matériau à ajouter.")
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de l'import des matériaux: {e}")
        raise
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur inattendue: {e}")
        raise
        
    finally:
        db.close()
        logger.debug("Connexion à la base de données fermée.")


if __name__ == "__main__":
    try:
        seed_materials()
    except Exception as e:
        logger.critical(f"Le script a échoué: {e}")
        exit(1)