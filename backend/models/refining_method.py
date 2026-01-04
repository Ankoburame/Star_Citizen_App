from sqlalchemy import Column, Integer, String
from database import Base

class RefiningMethod(Base):
    __tablename__ = "refining_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    time = Column(String(50), nullable=False)
    cost = Column(String(50), nullable=False)
    yield_rating = Column(String(50), nullable=False)
    description = Column(String(500))