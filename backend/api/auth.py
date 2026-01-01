"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.user import User
from schemas.auth import UserCreate, UserLogin, UserResponse, Token
from core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from schemas.auth import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()
security = HTTPBearer()


# ============================================================
# DEPENDENCY: Get Current User
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Récupère l'utilisateur actuel depuis le token JWT."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def require_role(allowed_roles: list[str]):
    """Dependency pour vérifier le rôle."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate, 
    current_user: User = Depends(require_role(["admin"])),  # ✅ ADMIN ONLY
    db: Session = Depends(get_db)
):
    """Créer un nouveau compte (ADMIN only)."""
    # Vérifier si username existe
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Vérifier si email existe
    if user_data.email and db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Créer user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Se connecter et obtenir un token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Créer token
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Récupérer les infos de l'utilisateur connecté."""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Récupérer tous les utilisateurs (ADMIN only)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

@router.post("/change-password")
def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Changer son mot de passe."""
    # Vérifier l'ancien mot de passe
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Changer le mot de passe
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/reset-password/{user_id}")
def reset_user_password(
    user_id: int,
    data: ResetPassword,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Reset le mot de passe d'un utilisateur (ADMIN only)."""
    # Trouver l'utilisateur
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Changer le mot de passe
    target_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    
    return {"message": f"Password reset successfully for user {target_user.username}"}