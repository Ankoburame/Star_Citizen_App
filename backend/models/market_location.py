from sqlalchemy import Column, Integer, String
from database import Base


class MarketLocation(Base):
    __tablename__ = "market_locations"

    id = Column(Integer, primary_key=True)

    # Exemple : "ARC-L1 Wide Forest Station"
    name = Column(String, nullable=False)

    # Exemple : "ArcCorp", "Hurston", "Crusader"
    system = Column(String, nullable=False)

    # Exemple : "ARC-L1", "Everus Harbor"
    station = Column(String, nullable=True)

    # Type : STATION | CITY | OUTPOST
    location_type = Column(String, nullable=False)
