from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    status = Column(String, default="ACTIVE")
    comment = Column(String)
