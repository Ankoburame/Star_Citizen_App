"""
Quantanium price service for Star Citizen App.
Specialized service for fetching and caching Quantanium prices from UEX Corp API.
"""

from datetime import datetime, timedelta
from typing import Optional

import requests
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from core.config import UEX_API_TOKEN
from models.market_price import MarketPrice

# UEX API configuration
UEX_API_URL = "https://api.uexcorp.space/2.0/commodities"
UEX_LOCATION = "UEX_ESTIMATED"
CACHE_TTL_HOURS = 12

# API request headers
HEADERS = {
    "Authorization": f"Bearer {UEX_API_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "StarCitizen-App/1.0",
}


def is_quantanium_cache_valid(db: Session) -> bool:
    """
    Check if cached Quantanium price is still valid.
    
    Args:
        db: Database session
        
    Returns:
        True if cache is valid (within TTL), False otherwise
    """
    cache_threshold = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)
    
    latest = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.source == "UEX",
            MarketPrice.location_string == UEX_LOCATION,
        )
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )
    
    if not latest:
        return False
    
    return latest.collected_at >= cache_threshold


def fetch_quantanium_price_from_uex() -> float:
    """
    Fetch Quantanium price from UEX commodities API.
    
    Searches for Quantanium by name or code in the commodities list
    and returns its sell price.
    
    Returns:
        Sell price for Quantanium
        
    Raises:
        RuntimeError: If API request fails, Quantanium not found,
                     or price_sell is null
    """
    response = requests.get(UEX_API_URL, headers=HEADERS, timeout=15)
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: HTTP {response.status_code}")
    
    payload = response.json()
    commodities = payload.get("data", [])
    
    # Search for Quantanium in commodities list
    for item in commodities:
        name = item.get("name", "").lower()
        code = item.get("code", "").lower()
        
        # Match by name or commodity code
        if "quantanium" in name or code in ("quan", "qtn"):
            price = item.get("price_sell")
            
            if price is None:
                raise RuntimeError("Quantanium found but price_sell is null")
            
            return float(price)
    
    # Debug information if Quantanium not found
    sample_names = [c.get("name") for c in commodities[:10]]
    raise RuntimeError(
        f"Quantanium not found in UEX commodities. "
        f"Sample commodities received: {sample_names}"
    )


def refresh_quantanium_price(db: Session, force: bool = False) -> None:
    """
    Refresh Quantanium price from UEX API.
    
    Fetches the latest Quantanium price and stores it in the database.
    Respects cache TTL unless forced.
    
    Args:
        db: Database session
        force: If True, bypass cache and force refresh
        
    Raises:
        RuntimeError: If Quantanium not found in materials table
                     or if API request fails
    """
    # Skip refresh if cache is valid and not forced
    if not force and is_quantanium_cache_valid(db):
        return
    
    # Find Quantanium material ID
    material_id = db.execute(
        text("SELECT id FROM materials WHERE name ILIKE 'quantanium' LIMIT 1")
    ).scalar()
    
    if not material_id:
        raise RuntimeError("Quantanium not found in materials table")
    
    # Fetch current price
    sell_price = fetch_quantanium_price_from_uex()
    
    # Create new price record
    price = MarketPrice(
        material_id=material_id,
        location=UEX_LOCATION,
        sell_price=sell_price,
        buy_price=None,
        source="UEX",
        updated_at=datetime.utcnow(),
    )
    
    db.add(price)
    db.commit()