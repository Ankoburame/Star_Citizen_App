from sqlalchemy import Column, Integer, String, JSON
from database import Base

class ScanSignature(Base):
    __tablename__ = "scan_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    signatures = Column(JSON, nullable=False)
    description = Column(String(500))