"""
Main FastAPI application for Star Citizen App.
Configures routes, middleware, and application lifecycle.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dashboard import router as dashboard_router
from api.materials import router as materials_router
from api.market import router as market_router  # ✅ NOUVEAU
from api.pricing import router as pricing_router
from api.production import router as production_router
from api.trade import router as trade_router
from api.ws_dashboard import router as ws_dashboard_router
from database import SessionLocal
from services.pricing_service import ensure_quantanium_price
from api.price_history import router as history_router
from api import market, price_history
from api import market, price_history, production


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
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.118:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HTTP ROUTES
# ============================================================================

app.include_router(materials_router, prefix="/materials", tags=["Materials"])
app.include_router(production_router, tags=["Production"])  # ✅ Sans prefix
app.include_router(trade_router, prefix="/trade", tags=["Trade"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(pricing_router, tags=["Pricing"])  # Already has /pricing prefix
app.include_router(market_router, prefix="/market", tags=["Market"])  # ✅ NOUVEAU
app.include_router(history_router, prefix="/history", tags=["Price History"])
app.include_router(market.router)
app.include_router(price_history.router)
app.include_router(market.router)
app.include_router(price_history.router)
app.include_router(production.router) 

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