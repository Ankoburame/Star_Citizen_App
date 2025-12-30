from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from core.config import UEX_API_TOKEN

from models.market_price import MarketPrice

UEX_API_URL = "https://api.uexcorp.uk/2.0/commodities"
CACHE_TTL_HOURS = 12
UEX_LOCATION = "UEX_ESTIMATED"

UEX_TOKEN = "5a3968ea34819ee5843fb698533e442ed9179708"

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
    url = "https://api.uexcorp.space/2.0/market/prices"

    response = requests.get(
        url,
        headers=HEADERS,
        params={"commodity_id": 37},
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(f"UEX API error {response.status_code}")

    payload = response.json()
    data = payload.get("data", [])

    if not data:
        raise RuntimeError("Aucune donnée UEX pour Quantanium")

    sell_prices = [
        row["price_sell"]
        for row in data
        if row.get("price_sell") is not None
    ]

    if not sell_prices:
        raise RuntimeError("Aucun price_sell exploitable")

    return float(max(sell_prices))




def refresh_quantanium_price(db: Session, force: bool = False):
    if not force and is_quantanium_cache_valid(db):
        return

    material_id = db.execute(
        text("SELECT id FROM materials WHERE name ILIKE '%quantanium%' LIMIT 1")
    ).scalar()

    if not material_id:
        raise RuntimeError("Quantanium introuvable dans la table materials")

    sell_price = fetch_quantanium_price_from_uex()
    now = datetime.utcnow()

    price = MarketPrice(
        material_id=material_id,
        location=UEX_LOCATION,
        sell_price=sell_price,
        buy_price=None,
        source="UEX",
        updated_at=now,
    )

    db.add(price)
    db.commit()
