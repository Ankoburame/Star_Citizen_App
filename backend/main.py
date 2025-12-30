from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import SessionLocal
from services.pricing_service import ensure_quantanium_price

from api.materials import router as materials_router
from api.production import router as production_router
from api.refining import router as refining_router
from api.trade import router as trade_router
from api.dashboard import router as dashboard_router
from api.pricing import router as pricing_router
from api.ws_dashboard import router as ws_dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 Warmup pricing (1 fois au démarrage)
    db = SessionLocal()
    try:
        ensure_quantanium_price(db)
    except Exception as e:
        print("⚠️ Quantanium init skipped:", e)

    finally:
        db.close()

    yield


app = FastAPI(lifespan=lifespan)

# =========================
# CORS
# =========================
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

# =========================
# ROUTES HTTP
# =========================
app.include_router(materials_router, prefix="/materials", tags=["Materials"])
app.include_router(production_router, prefix="/production", tags=["Production"])
app.include_router(refining_router, prefix="/refining", tags=["Refining"])
app.include_router(trade_router, prefix="/trade", tags=["Trade"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(pricing_router, prefix="/pricing", tags=["Pricing"])

# =========================
# WEBSOCKET
# =========================
app.include_router(ws_dashboard_router)
