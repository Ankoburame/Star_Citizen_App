from sqlalchemy.orm import Session
from models.market_price import MarketPrice


def get_best_sell_price(
    material_id: int,
    db: Session,
) -> float | None:
    price = (
        db.query(MarketPrice)
        .filter(MarketPrice.material_id == material_id)
        .filter(MarketPrice.sell_price.isnot(None))
        .order_by(MarketPrice.sell_price.desc())
        .first()
    )

    return price.sell_price if price else None
