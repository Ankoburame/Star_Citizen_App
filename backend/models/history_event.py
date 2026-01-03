"""
Model for history events with tags and crew tracking
"""

from sqlalchemy import Column, Integer, String, Text, ARRAY, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base


class HistoryEvent(Base):
    """
    History event model for tracking all user activities
    Supports tags and crew member tracking
    """
    __tablename__ = "history_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))
    tags = Column(ARRAY(Text))
    crew_members = Column(ARRAY(Integer))
    amount = Column(DECIMAL(12, 2))
    location = Column(String(100))
    event_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())