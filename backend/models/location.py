"""
Location model for Star Citizen stations, outposts, and trading locations.
Represents physical locations where materials can be bought or sold.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship

from database import Base


class Location(Base):
    """
    Represents a trading location in Star Citizen universe.
    
    Locations include:
    - Space stations (Port Olisar, Port Tressler, etc.)
    - Landing zones (Area18, Lorville, New Babbage, etc.)
    - Outposts and mining facilities
    - Rest stops
    
    Attributes:
        id: Primary key
        name: Display name of the location (e.g., "Port Olisar")
        code: Unique identifier code from UEX (e.g., "HURO1")
        system: Star system name (e.g., "Stanton")
        planet: Planet or moon name (e.g., "Crusader")
        location_type: Type of location (station, outpost, city, rest_stop, etc.)
        is_available: Whether the location is currently accessible in-game
        has_trade_terminals: Whether location has commodity trading terminals
        has_refinery: Whether location has refinery services
        faction: Controlling faction (e.g., "Crusader Industries", "Hurston Dynamics")
        latitude: Geographic coordinate (if applicable)
        longitude: Geographic coordinate (if applicable)
    """
    
    __tablename__ = "locations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String, nullable=False, unique=True, index=True)
    code = Column(String, unique=True, index=True)  # UEX code
    
    # Hierarchy
    system = Column(String, index=True)  # Stanton, Pyro, etc.
    planet = Column(String, index=True)  # Crusader, Hurston, ArcCorp, microTech
    moon = Column(String, nullable=True)  # Yela, Daymar, etc.
    
    # Type and characteristics
    location_type = Column(String, index=True)  # station, outpost, city, rest_stop
    is_available = Column(Boolean, default=True)  # Currently accessible in-game
    has_trade_terminals = Column(Boolean, default=False)
    has_refinery = Column(Boolean, default=False)
    has_shops = Column(Boolean, default=False)
    
    # Additional info
    faction = Column(String, nullable=True)  # Controlling faction
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationships
    market_prices = relationship("MarketPrice", back_populates="location_obj", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="location")  # ✅ NOUVEAU
    
    def __repr__(self):
        return f"<Location(name='{self.name}', system='{self.system}', type='{self.location_type}')>"
    
    @property
    def full_location_path(self) -> str:
        """
        Returns the full hierarchical path of the location.
        
        Examples:
            "Stanton > Crusader > Port Olisar"
            "Stanton > Hurston > Arial > HDMS-Lathan"
        """
        parts = [self.system, self.planet]
        
        if self.moon:
            parts.append(self.moon)
        
        parts.append(self.name)
        
        return " > ".join(filter(None, parts))
    
    @property
    def is_space_station(self) -> bool:
        """Returns True if location is a space station."""
        return self.location_type in ["station", "rest_stop"]
    
    @property
    def is_planetary(self) -> bool:
        """Returns True if location is on a planet or moon surface."""
        return self.location_type in ["city", "outpost", "mining_facility"]