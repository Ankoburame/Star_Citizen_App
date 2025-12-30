from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.market_price import MarketPrice
from services.uex_price_service import refresh_quantanium_price

PRICE_CACHE_TTL_HOURS = 12


# ======================================================
# PRIX GÉNÉRIQUE (utilisé par trade / refining / legacy)
# ======================================================
def get_latest_sell_price(material_id: int, db: Session) -> float | None:
    """
    Retourne le dernier prix de vente connu (toutes sources confondues).
    ⚠️ À utiliser pour le commerce, PAS pour le dashboard.
    """

    price = (
        db.query(MarketPrice)
        .filter(MarketPrice.material_id == material_id)
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )

    if not price:
        return None

    return price.sell_price


# ======================================================
# PRIX UEX — ESTIMATIF DASHBOARD
# ======================================================
def get_latest_uex_sell_price(material_id: int, db: Session) -> float | None:
    """
    Retourne le DERNIER prix de vente UEX pour un matériau donné.
    Utilisé pour la valeur estimée du stock.
    """

    price = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.material_id == material_id,
            MarketPrice.source == "UEX",
        )
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )

    if not price:
        return None

    return price.sell_price


# ======================================================
# GARDE-FOU AU DÉMARRAGE
# ======================================================
def ensure_quantanium_price(db: Session):
    """
    Assure qu'un prix Quantanium UEX existe en base.
    Le refresh réel est protégé par TTL.
    """

    latest_price = (
        db.query(MarketPrice)
        .filter(MarketPrice.source == "UEX")
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )

    if (
        latest_price
        and latest_price.collected_at
        >= datetime.utcnow() - timedelta(hours=PRICE_CACHE_TTL_HOURS)
    ):
        return

    refresh_quantanium_price(db)
