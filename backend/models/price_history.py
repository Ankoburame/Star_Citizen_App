"""
Price History model for tracking material price changes over time.
Stores daily snapshots of market prices for trend analysis.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class PriceHistory(Base):
    """
    Historical price records for materials.
    
    Captures daily snapshots of buy/sell prices at each location
    to enable trend analysis and historical charts.
    """
    __tablename__ = "price_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    
    # Price data
    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    
    # Metadata
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(50), default="UEX", nullable=False)
    
    # Relationships
    material = relationship("Material", back_populates="price_history")
    location = relationship("Location", back_populates="price_history")
    
    # Indexes for efficient queries
    __table_args__ = (
        # Find price history for specific material/location
        Index('idx_price_history_material_location', 'material_id', 'location_id'),
        # Time-based queries
        Index('idx_price_history_recorded_at', 'recorded_at'),
        # Combined for trend analysis
        Index('idx_price_history_lookup', 'material_id', 'location_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(material_id={self.material_id}, location_id={self.location_id}, recorded_at={self.recorded_at})>"