from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class StockEvent(Base):
    __tablename__ = "stock_events"

    id = Column(Integer, primary_key=True)

    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    unit_price = Column(Float, nullable=True)      # prix unitaire au moment T
    total_value = Column(Float, nullable=False, default=0.0)    # TOUJOURS renseigné

    event_type = Column(String, nullable=False)
    reference_type = Column(String, nullable=True)
    reference_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
