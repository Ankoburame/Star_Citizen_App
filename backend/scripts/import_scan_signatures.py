"""
Script d'import des signatures de scan dans la base de données.
Execute ce script pour peupler la table scan_signatures.
"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL non définie dans .env")
    sys.exit(1)

# Setup SQLAlchemy
Base = declarative_base()

class ScanSignature(Base):
    """Table pour les signatures de scan"""
    __tablename__ = "scan_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    signatures = Column(JSON, nullable=False)
    description = Column(String(500))

def main():
    print("🚀 Import des signatures de scan...")
    
    # Connexion DB
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Créer la table si elle n'existe pas
        Base.metadata.create_all(bind=engine)
        print("✅ Table scan_signatures vérifiée/créée")
        
        # Charger le JSON
        json_path = Path(__file__).parent.parent / "external_data" / "scan_signatures.json"
        if not json_path.exists():
            print(f"❌ Fichier non trouvé: {json_path}")
            sys.exit(1)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 Fichier chargé: {json_path}")
        
        # Supprimer les anciennes données
        deleted = session.query(ScanSignature).delete()
        print(f"🗑️  Suppression de {deleted} anciennes entrées")
        
        # Import Surface Deposits
        count = 0
        for deposit in data.get("surface_deposits", []):
            sig = ScanSignature(
                type=deposit["type"],
                category=deposit["category"],
                signatures=deposit["signatures"]
            )
            session.add(sig)
            count += 1
        
        # Import Space Ice
        for ice in data.get("space_ice", []):
            sig = ScanSignature(
                type=ice["type"],
                category=ice["category"],
                signatures=ice["signatures"]
            )
            session.add(sig)
            count += 1
        
        # Import Space Asteroids
        for asteroid in data.get("space_asteroids", []):
            sig = ScanSignature(
                type=asteroid["type"],
                category=asteroid["category"],
                signatures=asteroid["signatures"]
            )
            session.add(sig)
            count += 1
        
        # Import Salvage (avec description spéciale)
        salvage_data = data.get("salvage", {})
        if "debris" in salvage_data:
            sig = ScanSignature(
                type="Debris",
                category="Salvage",
                signatures=[],  # Pattern, pas de liste fixe
                description=salvage_data["debris"]["description"] + " - " + salvage_data["debris"]["pattern"]
            )
            session.add(sig)
            count += 1
        
        if "wrecks" in salvage_data:
            sig = ScanSignature(
                type="Wrecks",
                category="Salvage",
                signatures=[],
                description=salvage_data["wrecks"]["description"]
            )
            session.add(sig)
            count += 1
        
        # Commit
        session.commit()
        print(f"✅ {count} signatures importées avec succès!")
        
        # Vérification
        total = session.query(ScanSignature).count()
        print(f"📊 Total en base: {total} signatures")
        
        # Afficher quelques exemples
        print("\n📋 Exemples importés:")
        examples = session.query(ScanSignature).limit(5).all()
        for ex in examples:
            sig_preview = ex.signatures[:3] if isinstance(ex.signatures, list) and len(ex.signatures) > 3 else ex.signatures
            print(f"   - {ex.type} ({ex.category}): {sig_preview}...")
        
        print("\n🎉 Import terminé avec succès!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()