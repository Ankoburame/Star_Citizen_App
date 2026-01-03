"""
Router pour l'historique des événements avec tags et crew tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.history_event import HistoryEvent
from models.user import User

router = APIRouter(prefix="/stats/history", tags=["History"])


# ========================================
# SCHEMAS
# ========================================

class CrewMemberResponse(BaseModel):
    """Crew member info for display"""
    id: int
    username: str
    
    class Config:
        from_attributes = True


class HistoryEventCreate(BaseModel):
    """Schema for creating a new event"""
    title: str
    description: Optional[str] = None
    event_type: Optional[str] = None
    tags: List[str] = []
    crew_members: List[int] = []
    amount: Optional[float] = None
    location: Optional[str] = None
    event_date: datetime


class HistoryEventUpdate(BaseModel):
    """Schema for updating an event"""
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    tags: Optional[List[str]] = None
    crew_members: Optional[List[int]] = None
    amount: Optional[float] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None


class HistoryEventResponse(BaseModel):
    """Schema for event response with crew details"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    event_type: Optional[str]
    tags: List[str]
    crew_members_ids: List[int]
    crew_members_details: List[CrewMemberResponse]
    amount: Optional[float]
    location: Optional[str]
    event_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========================================
# ENDPOINTS
# ========================================

@router.get("/", response_model=List[HistoryEventResponse])
async def get_history_events(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    crew_member: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get history events with optional filters
    
    - tag: Filter by tag
    - crew_member: Filter by crew member user_id
    - search: Search in title and description
    """
    query = db.query(HistoryEvent).order_by(HistoryEvent.event_date.desc())
    
    # Filter by tag
    if tag:
        query = query.filter(HistoryEvent.tags.contains([tag]))
    
    # Filter by crew member
    if crew_member:
        query = query.filter(HistoryEvent.crew_members.contains([crew_member]))
    
    # Search in title and description
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (HistoryEvent.title.ilike(search_filter)) |
            (HistoryEvent.description.ilike(search_filter))
        )
    
    events = query.offset(skip).limit(limit).all()
    
    # Enrich with crew member details
    result = []
    for event in events:
        crew_details = []
        if event.crew_members:
            crew_users = db.query(User).filter(User.id.in_(event.crew_members)).all()
            crew_details = [
                CrewMemberResponse(id=u.id, username=u.username)
                for u in crew_users
            ]
        
        result.append(
            HistoryEventResponse(
                id=event.id,
                user_id=event.user_id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                tags=event.tags or [],
                crew_members_ids=event.crew_members or [],
                crew_members_details=crew_details,
                amount=event.amount,
                location=event.location,
                event_date=event.event_date,
                created_at=event.created_at
            )
        )
    
    return result


@router.get("/{event_id}", response_model=HistoryEventResponse)
async def get_history_event(event_id: int, db: Session = Depends(get_db)):
    """Get a single event by ID"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get crew member details
    crew_details = []
    if event.crew_members:
        crew_users = db.query(User).filter(User.id.in_(event.crew_members)).all()
        crew_details = [
            CrewMemberResponse(id=u.id, username=u.username)
            for u in crew_users
        ]
    
    return HistoryEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        tags=event.tags or [],
        crew_members_ids=event.crew_members or [],
        crew_members_details=crew_details,
        amount=event.amount,
        location=event.location,
        event_date=event.event_date,
        created_at=event.created_at
    )


@router.post("/", response_model=HistoryEventResponse)
async def create_history_event(
    event_data: HistoryEventCreate,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a new history event"""
    event = HistoryEvent(
        user_id=user_id,
        title=event_data.title,
        description=event_data.description,
        event_type=event_data.event_type,
        tags=event_data.tags,
        crew_members=event_data.crew_members,
        amount=event_data.amount,
        location=event_data.location,
        event_date=event_data.event_date
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Get crew member details
    crew_details = []
    if event.crew_members:
        crew_users = db.query(User).filter(User.id.in_(event.crew_members)).all()
        crew_details = [
            CrewMemberResponse(id=u.id, username=u.username)
            for u in crew_users
        ]
    
    return HistoryEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        event_type=event_data.event_type,
        tags=event.tags or [],
        crew_members_ids=event.crew_members or [],
        crew_members_details=crew_details,
        amount=event.amount,
        location=event.location,
        event_date=event.event_date,
        created_at=event.created_at
    )


@router.put("/{event_id}", response_model=HistoryEventResponse)
async def update_history_event(
    event_id: int,
    event_data: HistoryEventUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing event"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    # Get crew member details
    crew_details = []
    if event.crew_members:
        crew_users = db.query(User).filter(User.id.in_(event.crew_members)).all()
        crew_details = [
            CrewMemberResponse(id=u.id, username=u.username)
            for u in crew_users
        ]
    
    return HistoryEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        tags=event.tags or [],
        crew_members_ids=event.crew_members or [],
        crew_members_details=crew_details,
        amount=event.amount,
        location=event.location,
        event_date=event.event_date,
        created_at=event.created_at
    )


@router.delete("/{event_id}")
async def delete_history_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}


@router.get("/tags/available")
async def get_available_tags(db: Session = Depends(get_db)):
    """Get all unique tags used across events"""
    events = db.query(HistoryEvent).all()
    all_tags = set()
    for event in events:
        if event.tags:
            all_tags.update(event.tags)
    
    return {"tags": sorted(list(all_tags))}


@router.get("/users/available", response_model=List[CrewMemberResponse])
async def get_available_users(db: Session = Depends(get_db)):
    """Get all users available for crew selection"""
    users = db.query(User).all()
    return [CrewMemberResponse(id=u.id, username=u.username) for u in users]