"""
Script d'import des méthodes de raffinage dans la base de données.
Execute ce script pour peupler la table refining_methods.
"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String
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

class RefiningMethod(Base):
    """Table pour les méthodes de raffinage"""
    __tablename__ = "refining_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    time = Column(String(50), nullable=False)
    cost = Column(String(50), nullable=False)
    yield_rating = Column(String(50), nullable=False)  # "yield" est réservé en Python
    description = Column(String(500))

def main():
    print("🚀 Import des méthodes de raffinage...")
    
    # Connexion DB
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Créer la table si elle n'existe pas
        Base.metadata.create_all(bind=engine)
        print("✅ Table refining_methods vérifiée/créée")
        
        # Charger le JSON
        json_path = Path(__file__).parent.parent / "external_data" / "refining_methods.json"
        if not json_path.exists():
            print(f"❌ Fichier non trouvé: {json_path}")
            sys.exit(1)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 Fichier chargé: {json_path}")
        
        # Supprimer les anciennes données
        deleted = session.query(RefiningMethod).delete()
        print(f"🗑️  Suppression de {deleted} anciennes méthodes")
        
        # Import des méthodes
        count = 0
        for method_data in data:
            method = RefiningMethod(
                name=method_data["name"],
                time=method_data["time"],
                cost=method_data["cost"],
                yield_rating=method_data["yield"],
                description=method_data.get("description")
            )
            session.add(method)
            count += 1
        
        # Commit
        session.commit()
        print(f"✅ {count} méthodes importées avec succès!")
        
        # Vérification
        total = session.query(RefiningMethod).count()
        print(f"📊 Total en base: {total} méthodes")
        
        # Afficher toutes les méthodes
        print("\n📋 Méthodes importées:")
        methods = session.query(RefiningMethod).all()
        for m in methods:
            print(f"   ⚙️  {m.name}")
            print(f"      Time: {m.time} | Cost: {m.cost} | Yield: {m.yield_rating}")
            if m.description:
                print(f"      → {m.description}")
        
        print("\n🎉 Import terminé avec succès!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()