"""
Main FastAPI application for Star Citizen App.
Configures routes, middleware, and application lifecycle.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal
from services.pricing_service import ensure_quantanium_price

# Import routers
from routes import reference
from api import production, commerce, market, price_history, auth
from api.dashboard import router as dashboard_router
from api.materials import router as materials_router
from api.pricing import router as pricing_router
from api.trade import router as trade_router
from api.ws_dashboard import router as ws_dashboard_router
from routes import reference, history


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the application.
    Initializes Quantanium pricing data on startup.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application runtime
    """
    # Startup: Initialize pricing data
    db = SessionLocal()
    try:
        ensure_quantanium_price(db)
        print("✅ Quantanium price initialized")
    except Exception as e:
        print(f"⚠️  Quantanium initialization failed: {e}")
    finally:
        db.close()
    
    yield
    
    # Shutdown: cleanup would go here if needed


# Create FastAPI application
app = FastAPI(
    title="Star Citizen App API",
    description="Backend API for Star Citizen resource management",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://star-citizen-app.vercel.app",
        "http://localhost:3000",
        "*"  # Pour autoriser tout (dev)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HTTP ROUTES
# ============================================================================

# Authentication
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Reference data
app.include_router(reference.router)

# Dashboard & Materials
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(materials_router, prefix="/materials", tags=["Materials"])

# Production & Commerce
app.include_router(production.router)
app.include_router(commerce.router)

# Market & Pricing
app.include_router(market.router)
app.include_router(pricing_router, tags=["Pricing"])
app.include_router(price_history.router)

# Trade
app.include_router(trade_router, prefix="/trade", tags=["Trade"])

# History
app.include_router(history.router)

# ============================================================================
# WEBSOCKET ROUTES
# ============================================================================

app.include_router(ws_dashboard_router, tags=["WebSocket"])


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Simple status message confirming API is running
    """
    return {"status": "ok", "message": "Star Citizen App API is running"}