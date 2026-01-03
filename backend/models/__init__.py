"""
Models package initialization.
Imports all models in the correct order to avoid circular import issues.
"""

# Import base first
from database import Base

# Import models in dependency order
from models.user import User
from models.material import Material
from models.refinery import Refinery
from models.location import Location
from models.market_price import MarketPrice
from models.price_history import PriceHistory
from models.refining_job import RefiningJob, RefiningJobMaterial
from models.inventory import Inventory
from models.sale import Sale
from models.commerce import CommerceTransaction
from models.freight import Freight
from models.market_location import MarketLocation
from models.run import Run
from models.session import Session
from models.stock_event import StockEvent
from models.stock import Stock
from models.trade_run import TradeRun
from models.scan_signature import ScanSignature
from models.refinery_bonus import RefineryBonus
from models.refining_method import RefiningMethod
from models.history_event import HistoryEvent
# Export all models for easy import
__all__ = [
    "Base",
    "User",
    "Material",
    "Refinery",
    "Location",
    "MarketPrice",
    "PriceHistory",
    "RefiningJob",
    "RefiningJobMaterial",
    "Inventory",
    "Sale",
    "CommerceTransaction",
    "Freight",
    "MarketLocation",
    "Run",
    "Session",
    "StockEvent",
    "Stock",
    "TradeRun",
    "CargoRun",
    "ScanSignature",
    "RefineryBonus",
    "RefiningMethod",
    "HistoryEvent",
]