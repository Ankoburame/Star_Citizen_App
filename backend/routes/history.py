"""
Router pour l'historique des événements avec tags, crew tracking, et payout
ROUTES - PAS API
"""

# 1. Standard library
from datetime import datetime
from typing import List, Optional
import os

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 3. Local
from database import get_db
from models.history_event import HistoryEvent
from models.user import User

router = APIRouter(prefix="/stats/history", tags=["History"])

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

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
    """Schema for updating an event - TAGS ONLY"""
    tags: Optional[List[str]] = None


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


class CrewShareCalculation(BaseModel):
    """Individual crew member share for payout"""
    user_id: int
    username: str
    share_amount: float
    event_count: int


class PayoutCalculation(BaseModel):
    """Complete payout calculation"""
    total_profit: float
    service_fee: float
    net_amount: float
    crew_shares: List[CrewShareCalculation]
    selected_events: List[int]


class PayoutRequest(BaseModel):
    """Request to calculate payout"""
    event_ids: List[int]


class PayoutTransaction(BaseModel):
    """Single payout transaction"""
    recipient_id: int
    amount: float
    note: Optional[str] = None


class PayoutExecuteRequest(BaseModel):
    """Execute payout to crew"""
    event_ids: List[int]
    transactions: List[PayoutTransaction]


# ========================================
# HELPER FUNCTION
# ========================================

def _build_event_response(event: HistoryEvent, db: Session) -> HistoryEventResponse:
    """Build event response with crew details"""
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


# ========================================
# AUTH
# ========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Vérifie le token JWT et retourne l'utilisateur"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# ========================================
# HISTORY EVENTS ENDPOINTS
# ========================================

@router.get("", response_model=List[HistoryEventResponse])
async def get_history_events(
    tag: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history events with filters"""
    query = db.query(HistoryEvent)
    
    # Filter by user if not admin
    if current_user.role != "admin":
        query = query.filter(HistoryEvent.user_id == current_user.id)
    
    # Apply filters
    if tag:
        query = query.filter(HistoryEvent.tags.contains([tag]))
    if event_type:
        query = query.filter(HistoryEvent.event_type == event_type)
    if start_date:
        query = query.filter(HistoryEvent.event_date >= start_date)
    if end_date:
        query = query.filter(HistoryEvent.event_date <= end_date)
    
    events = query.order_by(HistoryEvent.event_date.desc()).all()
    
    return [_build_event_response(event, db) for event in events]


@router.get("/{event_id}", response_model=HistoryEventResponse)
async def get_history_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single event by ID"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return _build_event_response(event, db)


@router.put("/{event_id}", response_model=HistoryEventResponse)
async def update_history_event_tags(
    event_id: int,
    event_data: HistoryEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ONLY tags for an event"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update ONLY tags
    if event_data.tags is not None:
        event.tags = event_data.tags
    
    db.commit()
    db.refresh(event)
    
    return _build_event_response(event, db)


@router.delete("/{event_id}")
async def delete_history_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an event (admin only)"""
    event = db.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}


# ========================================
# SNAPSHOT ENDPOINT
# ========================================

@router.post("/snapshot")
async def create_history_snapshot(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a financial snapshot from history events.
    Returns total profit, total cost, net profit.
    """
    # Get all events for current user
    query = db.query(HistoryEvent)
    
    if current_user.role != "admin":
        query = query.filter(HistoryEvent.user_id == current_user.id)
    
    events = query.all()
    
    # Calculate totals
    total_revenue = sum(e.amount for e in events if e.amount and e.amount > 0)
    total_cost = abs(sum(e.amount for e in events if e.amount and e.amount < 0))
    net_profit = total_revenue - total_cost
    
    # Count events by type
    event_counts = {
        "refining": len([e for e in events if e.event_type == "refining"]),
        "sale": len([e for e in events if e.event_type == "sale"]),
        "payout": len([e for e in events if e.event_type == "payout"]),
        "total": len(events)
    }
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "snapshot_date": datetime.utcnow(),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin": round((net_profit / total_revenue * 100) if total_revenue > 0 else 0, 2),
        "event_counts": event_counts
    }


# ========================================
# CREW PAYOUT ENDPOINTS
# ========================================

@router.get("/payout/events")
async def get_profitable_crew_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all profitable events with crew members.
    Used to populate the event selection list.
    """
    query = db.query(HistoryEvent).filter(
        HistoryEvent.amount > 0  # Profitable only
    )
    
    if current_user.role != "admin":
        query = query.filter(HistoryEvent.user_id == current_user.id)
    
    events = query.order_by(HistoryEvent.event_date.desc()).all()
    
    # Filter events with crew (more than 1 member)
    crew_events = []
    for event in events:
        if event.crew_members and len(event.crew_members) > 1:
            crew_events.append({
                "id": event.id,
                "title": event.title,
                "amount": float(event.amount),
                "event_date": event.event_date,
                "crew_count": len(event.crew_members),
                "tags": event.tags or []
            })
    
    return {"events": crew_events}


@router.post("/payout/calculate", response_model=PayoutCalculation)
async def calculate_crew_payout(
    request: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate crew payout distribution for selected events.
    Returns equal shares for all crew members involved.
    """
    if not request.event_ids:
        raise HTTPException(status_code=400, detail="No events selected")
    
    # Get selected events
    events = db.query(HistoryEvent).filter(
        HistoryEvent.id.in_(request.event_ids)
    ).all()
    
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    
    # Check ownership if not admin
    if current_user.role != "admin":
        for event in events:
            if event.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate total profit
    total_profit = sum(e.amount for e in events if e.amount and e.amount > 0)
    
    # Service fee (0.5% like in-game)
    service_fee = total_profit * 0.005
    net_amount = total_profit - service_fee
    
    # Get all unique crew members
    crew_map = {}  # {user_id: {username, event_count}}
    
    for event in events:
        if event.crew_members:
            for member_id in event.crew_members:
                if member_id not in crew_map:
                    # Get user
                    user = db.query(User).filter(User.id == member_id).first()
                    if user:
                        crew_map[member_id] = {
                            "username": user.username,
                            "event_count": 0
                        }
                
                if member_id in crew_map:
                    crew_map[member_id]["event_count"] += 1
    
    # Calculate equal shares
    if not crew_map:
        raise HTTPException(status_code=400, detail="No crew members found in selected events")
    
    share_amount = net_amount / len(crew_map)
    
    crew_shares = [
        CrewShareCalculation(
            user_id=user_id,
            username=data["username"],
            share_amount=round(share_amount, 2),
            event_count=data["event_count"]
        )
        for user_id, data in crew_map.items()
    ]
    
    return PayoutCalculation(
        total_profit=round(total_profit, 2),
        service_fee=round(service_fee, 2),
        net_amount=round(net_amount, 2),
        crew_shares=crew_shares,
        selected_events=request.event_ids
    )


@router.post("/payout/execute")
async def execute_crew_payout(
    request: PayoutExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute payout - creates history events for each transaction.
    This logs the payout but doesn't handle actual aUEC transfer.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")
    
    # Verify ownership of events
    events = db.query(HistoryEvent).filter(
        HistoryEvent.id.in_(request.event_ids)
    ).all()
    
    if current_user.role != "admin":
        for event in events:
            if event.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create history events for each payout
    created_events = []
    
    for transaction in request.transactions:
        # Get recipient
        recipient = db.query(User).filter(User.id == transaction.recipient_id).first()
        if not recipient:
            continue
        
        # Create payout event
        payout_event = HistoryEvent()
        payout_event.user_id = int(current_user.id)
        payout_event.title = f"Payout - {recipient.username}"
        payout_event.description = f"Crew payout sent to {recipient.username}. {transaction.note or ''}".strip()
        payout_event.event_type = "payout"
        payout_event.tags = ["payout", "crew"]
        payout_event.crew_members = [int(current_user.id), int(recipient.id)]
        payout_event.amount = -transaction.amount
        payout_event.location = None
        payout_event.event_date = datetime.utcnow()
        
        db.add(payout_event)
        created_events.append(payout_event)
    
    db.commit()
    
    return {
        "message": f"Payout executed: {len(created_events)} transactions created",
        "transactions_count": len(created_events)
    }


# ========================================
# UTILITY ENDPOINTS
# ========================================

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