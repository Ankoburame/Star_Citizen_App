from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class RefineryBonus(Base):
    __tablename__ = "refinery_bonuses"
    
    id = Column(Integer, primary_key=True, index=True)
    refinery_id = Column(Integer, ForeignKey("refineries.id"), nullable=False)
    material_name = Column(String(100), nullable=False, index=True)
    bonus_percentage = Column(Integer, nullable=False)