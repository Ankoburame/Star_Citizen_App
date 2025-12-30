from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    unit = Column(String, nullable=False)

    is_mineable = Column(Boolean, default=False)
    is_salvage = Column(Boolean, default=False)
    is_trade_good = Column(Boolean, default=False)

    # --- ÉCONOMIE ---
    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
