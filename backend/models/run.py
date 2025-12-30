from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from datetime import datetime

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    raw_quantity = Column(Integer, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
