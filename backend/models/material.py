from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String)
    unit = Column(String, default="SCU")
    is_mineable = Column(Boolean, default=False)
    is_salvage = Column(Boolean, default=False)
    is_trade_good = Column(Boolean, default=False)
    sell_price = Column(Float, nullable=True)
    
    # ✅ AJOUTEZ CETTE LIGNE
    market_prices = relationship("MarketPrice", back_populates="material")