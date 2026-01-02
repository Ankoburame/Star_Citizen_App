"""
Model pour l'inventaire (Inventory/Stack).
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from database import Base


class Inventory(Base):
    """Inventaire de matériaux raffinés par location."""
    
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint('refinery_id', 'material_id', 'user_id', name='uq_inventory_refinery_material_user'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    refinery_id = Column(Integer, ForeignKey("refineries.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    
    # Quantité
    quantity = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(10), default="SCU")
    
    # Métadonnées
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    refinery = relationship("Refinery", back_populates="inventory")
    material = relationship("Material")
    
    def __repr__(self):
        return f"<Inventory(refinery='{self.refinery.name if self.refinery else 'N/A'}', material='{self.material.name if self.material else 'N/A'}', qty={self.quantity})>"
    
    @property
    def estimated_value(self):
        """Valeur estimée basée sur le prix de vente moyen."""
        if self.material and hasattr(self.material, 'avg_sell_price') and self.material.avg_sell_price:
            return float(self.quantity) * float(self.material.avg_sell_price)
        return 0.0
    
    def add_quantity(self, amount: float):
        """Ajoute une quantité à l'inventaire."""
        self.quantity += amount
        self.last_updated = datetime.utcnow()
    
    def remove_quantity(self, amount):
        if self.quantity >= Decimal(str(amount)):
            self.quantity -= Decimal(str(amount))
            self.last_updated = datetime.utcnow()
            return True
        return False