"""
UEX price service for Star Citizen App.
Handles fetching and caching of commodity prices from UEX Corp API.

Note: This module appears to be deprecated in favor of uex/quantanium_service.py
"""

from datetime import datetime, timedelta
from typing import Optional

import requests
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from core.config import UEX_API_TOKEN
from models.market_price import MarketPrice

# UEX API configuration
UEX_API_URL = "https://api.uexcorp.space/2.0/market/prices"
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
            MarketPrice.location == UEX_LOCATION,
        )
        .order_by(desc(MarketPrice.collected_at))
        .first()
    )
    
    if not latest:
        return False
    
    return latest.collected_at >= cache_threshold


def fetch_quantanium_price_from_uex() -> float:
    """
    Fetch Quantanium price from UEX API.
    
    Returns:
        Maximum sell price for Quantanium across all locations
        
    Raises:
        RuntimeError: If API request fails or no valid price data is found
    """
    response = requests.get(
        UEX_API_URL,
        headers=HEADERS,
        params={"commodity_id": 37},  # Quantanium commodity ID
        timeout=15,
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"UEX API error: HTTP {response.status_code}")
    
    payload = response.json()
    data = payload.get("data", [])
    
    if not data:
        raise RuntimeError("No UEX data available for Quantanium")
    
    # Extract all valid sell prices
    sell_prices = [
        row["price_sell"]
        for row in data
        if row.get("price_sell") is not None
    ]
    
    if not sell_prices:
        raise RuntimeError("No valid sell prices found for Quantanium")
    
    return float(max(sell_prices))


def refresh_quantanium_price(db: Session, force: bool = False) -> None:
    """
    Refresh Quantanium price from UEX API.
    
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
        text("SELECT id FROM materials WHERE name ILIKE '%quantanium%' LIMIT 1")
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