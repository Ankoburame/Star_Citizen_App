"""
Script pour vérifier la structure de la table refineries existante
"""

from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("🔍 Structure de la table 'refineries':\n")

if 'refineries' in inspector.get_table_names():
    columns = inspector.get_columns('refineries')
    print("Colonnes existantes:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
else:
    print("❌ Table 'refineries' n'existe pas")