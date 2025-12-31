from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class CargoRun(Base):
    __tablename__ = "cargo_runs"

    id = Column(Integer, primary_key=True, index=True)
    commodity_name = Column(String(200), nullable=False)
    buy_location = Column(String(200), nullable=False)
    sell_location = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    total_investment = Column(Float, nullable=False)
    expected_profit = Column(Float, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "commodity_name": self.commodity_name,
            "buy_location": self.buy_location,
            "sell_location": self.sell_location,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "total_investment": self.total_investment,
            "expected_profit": self.expected_profit,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "notes": self.notes
        }