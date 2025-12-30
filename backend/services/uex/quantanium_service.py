from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from sqlalchemy import desc, text

from models.market_price import MarketPrice
from core.config import UEX_API_TOKEN

UEX_API_URL = "https://api.uexcorp.space/2.0/commodities"
UEX_LOCATION = "UEX_ESTIMATED"
CACHE_TTL_HOURS = 12

HEADERS = {
    "Authorization": f"Bearer {UEX_API_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "StarCitizen-App/1.0",
}


def is_quantanium_cache_valid(db: Session) -> bool:
    latest = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.source == "UEX",
            MarketPrice.location == UEX_LOCATION,
        )
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )

    if not latest:
        return False

    return latest.collected_at >= datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)


def fetch_quantanium_price_from_uex() -> float:
    url = "https://api.uexcorp.space/2.0/commodities"

    response = requests.get(url, headers=HEADERS, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(f"UEX API error {response.status_code}")

    payload = response.json()
    commodities = payload.get("data", [])

    for item in commodities:
        name = item.get("name", "").lower()
        code = item.get("code", "").lower()

        # ✅ MATCH LARGE ET RÉALISTE
        if "quantanium" in name or code in ("quan", "qtn"):
            price = item.get("price_sell")

            if price is None:
                raise RuntimeError("Quantanium trouvé mais price_sell est NULL")

            return float(price)

    # 🔥 DEBUG ULTIME (si ça arrive encore)
    sample = [c.get("name") for c in commodities[:10]]
    raise RuntimeError(
        f"Quantanium introuvable. "
        f"Exemples commodities reçues: {sample}"
    )

def refresh_quantanium_price(db: Session, force: bool = False):
    if not force and is_quantanium_cache_valid(db):
        return

    material_id = db.execute(
        text("SELECT id FROM materials WHERE name ILIKE 'quantanium' LIMIT 1")
    ).scalar()

    if not material_id:
        raise RuntimeError("Quantanium introuvable dans la table materials")

    sell_price = fetch_quantanium_price_from_uex()

    price = MarketPrice(
        material_id=material_id,
        location=UEX_LOCATION,
        sell_price=sell_price,   # JAMAIS NULL
        buy_price=None,
        source="UEX",
        updated_at=datetime.utcnow(),
    )

    db.add(price)
    db.commit()
