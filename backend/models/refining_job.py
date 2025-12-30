"""
Model pour les jobs de raffinerie (RefiningJob).
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from database import Base


class RefiningJob(Base):
    """Job de raffinerie (mining ou salvage)."""
    
    __tablename__ = "refining_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    refinery_id = Column(Integer, ForeignKey("refineries.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    
    # Détails
    job_type = Column(String(20), default="mining")  # 'mining' ou 'salvage'
    total_cost = Column(Numeric(12, 2))
    processing_time = Column(Integer)  # En minutes
    
    # Status
    status = Column(String(20), default="processing", index=True)  # processing, ready, collected, cancelled
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, index=True)
    collected_at = Column(DateTime)
    
    # Métadonnées
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    refinery = relationship("Refinery", back_populates="refining_jobs")
    materials = relationship("RefiningJobMaterial", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RefiningJob(id={self.id}, refinery='{self.refinery.name if self.refinery else 'N/A'}', status='{self.status}')>"
    
    @property
    def seconds_remaining(self):
        """Secondes restantes jusqu'à la fin du raffinage."""
        if self.end_time and self.status == "processing":
            delta = self.end_time - datetime.utcnow()
            return max(0, int(delta.total_seconds()))
        return 0
    
    @property
    def progress_percentage(self):
        """Pourcentage de progression (0-100)."""
        if not self.end_time or self.status != "processing":
            return 100 if self.status == "ready" else 0
        
        total = (self.end_time - self.start_time).total_seconds()
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        
        if total <= 0:
            return 100
        
        progress = min(100, max(0, (elapsed / total) * 100))
        return round(progress, 1)
    
    @property
    def is_ready(self):
        """Le job est-il prêt à être récupéré?"""
        return self.status == "processing" and self.end_time and datetime.utcnow() >= self.end_time
    
    def check_and_update_status(self):
        """Met à jour le status si le job est terminé."""
        if self.is_ready:
            self.status = "ready"
            return True
        return False


class RefiningJobMaterial(Base):
    """Matériau contenu dans un job de raffinerie."""
    
    __tablename__ = "refining_job_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("refining_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Quantités
    quantity_refined = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(10), default="SCU")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    job = relationship("RefiningJob", back_populates="materials")
    material = relationship("Material")
    
    def __repr__(self):
        return f"<RefiningJobMaterial(job_id={self.job_id}, material='{self.material.name if self.material else 'N/A'}', qty={self.quantity_refined})>"