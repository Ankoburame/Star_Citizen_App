"""
Models package initialization.
Imports all models in the correct order to avoid circular import issues.
"""

# Import base first
from database import Base

# Import models in dependency order
from models.material import Material
from models.market_price import MarketPrice

# Export all models for easy import
__all__ = [
    "Base",
    "Material",
    "MarketPrice",
    "Location",
]
