"""
Model pour les raffineries (Refinery).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Refinery(Base):
    """Raffinerie disponible dans le jeu."""
    
    __tablename__ = "refineries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    system = Column(String(50), nullable=False, index=True)
    location = Column(String(100))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    refining_jobs = relationship("RefiningJob", back_populates="refinery", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="refinery", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="refinery_source", foreign_keys="Sale.refinery_source_id")
    
    def __repr__(self):
        return f"<Refinery(name='{self.name}', system='{self.system}')>"