"""
Script d'initialisation de la base de données.
Crée toutes les tables définies dans les modèles SQLAlchemy.
"""

import os
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine

# Import ALL models pour que SQLAlchemy les connaisse
print("📦 Importing models...")

try:
    from models.models import CargoRun
    print("  ✅ CargoRun")
except Exception as e:
    print(f"  ⚠️ CargoRun: {e}")

try:
    from models.material import Material
    print("  ✅ Material")
except Exception as e:
    print(f"  ⚠️ Material: {e}")

try:
    from models.location import Location
    print("  ✅ Location")
except Exception as e:
    print(f"  ⚠️ Location: {e}")

try:
    from models.market_price import MarketPrice
    print("  ✅ MarketPrice")
except Exception as e:
    print(f"  ⚠️ MarketPrice: {e}")

try:
    from models.price_history import PriceHistory
    print("  ✅ PriceHistory")
except Exception as e:
    print(f"  ⚠️ PriceHistory: {e}")

try:
    from models.refinery import Refinery
    print("  ✅ Refinery")
except Exception as e:
    print(f"  ⚠️ Refinery: {e}")

try:
    from models.refining_job import RefiningJob, RefiningJobMaterial
    print("  ✅ RefiningJob, RefiningJobMaterial")
except Exception as e:
    print(f"  ⚠️ RefiningJob: {e}")

try:
    from models.inventory import Inventory
    print("  ✅ Inventory")
except Exception as e:
    print(f"  ⚠️ Inventory: {e}")

try:
    from models.sale import Sale
    print("  ✅ Sale")
except Exception as e:
    print(f"  ⚠️ Sale: {e}")

try:
    from models.commerce import CommerceTransaction
    print("  ✅ CommerceTransaction")
except Exception as e:
    print(f"  ⚠️ CommerceTransaction: {e}")

try:
    from models.freight import Freight
    print("  ✅ Freight")
except Exception as e:
    print(f"  ⚠️ Freight: {e}")

try:
    from models.run import Run
    print("  ✅ Run")
except Exception as e:
    print(f"  ⚠️ Run: {e}")

try:
    from models.session import Session
    print("  ✅ Session")
except Exception as e:
    print(f"  ⚠️ Session: {e}")

try:
    from models.stock import Stock
    print("  ✅ Stock")
except Exception as e:
    print(f"  ⚠️ Stock: {e}")

try:
    from models.stock_event import StockEvent
    print("  ✅ StockEvent")
except Exception as e:
    print(f"  ⚠️ StockEvent: {e}")

try:
    from models.trade_run import TradeRun
    print("  ✅ TradeRun")
except Exception as e:
    print(f"  ⚠️ TradeRun: {e}")

try:
    from models.market_location import MarketLocation
    print("  ✅ MarketLocation")
except Exception as e:
    print(f"  ⚠️ MarketLocation: {e}")

print("\n🔨 Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

print("\n📊 Listing created tables...")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Found {len(tables)} tables:")
for table in sorted(tables):
    print(f"  - {table}")