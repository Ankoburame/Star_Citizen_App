"""
Model pour les ventes (Sale).
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Sale(Base):
    """Vente de matériaux."""
    
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    
    # Détails de la vente
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity_sold = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(10), default="SCU")
    
    # Prix
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_revenue = Column(Numeric(12, 2), nullable=False)
    
    # Coûts
    refining_cost = Column(Numeric(12, 2), default=0)
    
    # Locations
    sale_location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), index=True)
    refinery_source_id = Column(Integer, ForeignKey("refineries.id", ondelete="SET NULL"))
    
    # Métadonnées
    sale_date = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    material = relationship("Material")
    sale_location = relationship("Location", foreign_keys=[sale_location_id])
    refinery_source = relationship("Refinery", back_populates="sales", foreign_keys=[refinery_source_id])
    
    def __repr__(self):
        return f"<Sale(id={self.id}, material='{self.material.name if self.material else 'N/A'}', qty={self.quantity_sold}, revenue={self.total_revenue})>"
    
    @property
    def profit(self):
        """Profit net (revenu - coût de raffinage)."""
        return float(self.total_revenue) - float(self.refining_cost or 0)
    
    @property
    def profit_percentage(self):
        """Pourcentage de profit par rapport au coût."""
        if self.refining_cost and self.refining_cost > 0:
            return round((self.profit / float(self.refining_cost)) * 100, 2)
        return 0.0