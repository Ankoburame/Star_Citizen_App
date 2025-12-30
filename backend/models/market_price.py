from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    location = Column(String, nullable=False)

    sell_price = Column(Float, nullable=True)
    buy_price = Column(Float, nullable=True)

    source = Column(String, nullable=True)
    collected_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
