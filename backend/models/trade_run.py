from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class TradeRun(Base):
    __tablename__ = "trade_runs"

    id = Column(Integer, primary_key=True)

    material_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)

    buy_location = Column(String, nullable=False)
    sell_location = Column(String, nullable=False)

    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
