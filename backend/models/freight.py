from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Freight(Base):
    __tablename__ = "freight"

    id = Column(Integer, primary_key=True)
    origin = Column(String)
    destination = Column(String)
    ship = Column(String)
    capacity_scu = Column(Integer)
    departure_at = Column(DateTime)
    arrival_at = Column(DateTime)
    status = Column(String)
