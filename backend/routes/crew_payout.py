"""
Crew Payout Router - Profit distribution
ROUTES - Standalone router pour /stats/crew-payout
"""

from datetime import datetime
from typing import List
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.history_event import HistoryEvent
from models.user import User

router = APIRouter(prefix="/stats/crew-payout", tags=["Crew Payout"])

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


# ========================================
# SCHEMAS
# ========================================

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
    note: str | None = None


class PayoutExecuteRequest(BaseModel):
    """Execute payout to crew"""
    event_ids: List[int]
    transactions: List[PayoutTransaction]


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
# ENDPOINTS
# ========================================

@router.get("/profitable-events")
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


@router.post("/calculate", response_model=PayoutCalculation)
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


@router.post("/execute")
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
        
        # ✅ CREATE PAYOUT EVENT WITH EXPLICIT ASSIGNMENT
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