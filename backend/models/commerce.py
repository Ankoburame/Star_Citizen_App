from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from datetime import datetime

class CommerceTransaction(Base):
    __tablename__ = "commerce_transactions"

    id = Column(Integer, primary_key=True)
    freight_id = Column(Integer, ForeignKey("freight.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Integer)
    unit_price = Column(Integer)
    type = Column(String)  # BUY / SELL
    market = Column(String)
    executed_at = Column(DateTime, default=datetime.utcnow)
