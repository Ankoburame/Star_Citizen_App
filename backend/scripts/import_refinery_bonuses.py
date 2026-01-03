"""
Script d'import des bonus/malus de raffineries (VERSION CORRIGÉE)
Compatible avec la structure existante de la table refineries
"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
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

class Refinery(Base):
    """Table des raffineries (structure existante)"""
    __tablename__ = "refineries"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    system = Column(String(50), nullable=False)
    location = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class RefineryBonus(Base):
    """Table pour les bonus/malus de raffineries"""
    __tablename__ = "refinery_bonuses"
    
    id = Column(Integer, primary_key=True, index=True)
    refinery_id = Column(Integer, ForeignKey("refineries.id"), nullable=False)
    material_name = Column(String(100), nullable=False, index=True)
    bonus_percentage = Column(Integer, nullable=False)  # Peut être négatif (malus)

def main():
    print("🚀 Import des bonus de raffineries...")
    
    # Connexion DB
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Créer les tables si elles n'existent pas
        Base.metadata.create_all(bind=engine)
        print("✅ Tables vérifiées/créées")
        
        # Charger le JSON
        json_path = Path(__file__).parent.parent / "external_data" / "refinery_bonuses.json"
        if not json_path.exists():
            print(f"❌ Fichier non trouvé: {json_path}")
            sys.exit(1)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 Fichier chargé: {json_path}")
        
        # Supprimer les anciens bonus
        deleted_bonuses = session.query(RefineryBonus).delete()
        print(f"🗑️  Suppression de {deleted_bonuses} anciens bonus")
        
        # Supprimer les anciennes raffineries
        deleted_refineries = session.query(Refinery).delete()
        print(f"🗑️  Suppression de {deleted_refineries} anciennes raffineries")
        
        session.commit()
        
        # Import des raffineries et bonus
        total_refineries = 0
        total_bonuses = 0
        
        for ref_data in data.get("refineries", []):
            # Créer le nom complet
            # Format: "CODE - Full Name" pour pouvoir retrouver le code
            # Ex: "CRU-L1 - CRU-L1 Ambitious Dream Station"
            full_name = f"{ref_data['code']} - {ref_data['name']}"
            
            # Créer la raffinerie
            refinery = Refinery(
                name=full_name,  # On met le code dans le nom
                system=ref_data["system"],
                location=ref_data.get("parent"),
                is_active=True
            )
            session.add(refinery)
            session.flush()  # Pour obtenir l'ID
            total_refineries += 1
            
            # Ajouter les bonus/malus
            for material_name, bonus_value in ref_data.get("bonuses", {}).items():
                bonus = RefineryBonus(
                    refinery_id=refinery.id,
                    material_name=material_name,
                    bonus_percentage=bonus_value
                )
                session.add(bonus)
                total_bonuses += 1
        
        # Commit
        session.commit()
        print(f"✅ {total_refineries} raffineries importées!")
        print(f"✅ {total_bonuses} bonus/malus importés!")
        
        # Vérification
        refineries_count = session.query(Refinery).count()
        bonuses_count = session.query(RefineryBonus).count()
        print(f"\n📊 Total en base:")
        print(f"   - {refineries_count} raffineries")
        print(f"   - {bonuses_count} bonus/malus")
        
        # Afficher quelques exemples
        print("\n📋 Exemples importés:")
        examples = session.query(Refinery).limit(5).all()
        for ref in examples:
            # Extraire le code du nom
            code = ref.name.split(" - ")[0] if " - " in ref.name else ref.name[:10]
            bonuses = session.query(RefineryBonus).filter(RefineryBonus.refinery_id == ref.id).limit(3).all()
            print(f"\n   🏭 [{code}] {ref.location} ({ref.system}):")
            for b in bonuses:
                sign = "+" if b.bonus_percentage > 0 else ""
                print(f"      - {b.material_name}: {sign}{b.bonus_percentage}%")
        
        print("\n🎉 Import terminé avec succès!")
        print("\n💡 Note: Les codes (CRU-L1, HUR-L3, etc.) sont inclus dans le nom de la raffinerie")
        print("   Format: 'CODE - Full Name'")
        
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