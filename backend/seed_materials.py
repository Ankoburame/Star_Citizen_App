from database import SessionLocal
from models.material import Material

MATERIALS = [
    # Minage
    ("Stileron", "mineral", "SCU", True, False, False),
    ("Quantanium", "mineral", "SCU", True, False, False),
    ("Riccite", "mineral", "SCU", True, False, False),
    ("Salvrilium", "mineral", "SCU", True, False, False),
    ("Taranite", "mineral", "SCU", True, False, True),
    ("Lindinium", "mineral", "SCU", True, False, False),
    ("Bexalite", "mineral", "SCU", True, False, True),
    ("Gold", "mineral", "SCU", True, False, True),
    ("Borase", "mineral", "SCU", True, False, False),
    ("Laranite", "mineral", "SCU", True, False, True),
    ("Beryl", "mineral", "SCU", True, False, True),
    ("Agricium", "mineral", "SCU", True, False, True),
    ("Hephaestanite", "mineral", "SCU", True, False, True),
    ("Ice", "mineral", "SCU", True, False, False),
    ("Tungsten", "mineral", "SCU", True, False, True),
    ("Titanium", "mineral", "SCU", True, False, True),
    ("Iron", "mineral", "SCU", True, False, True),
    ("Quartz", "mineral", "SCU", True, False, True),
    ("Torite", "mineral", "SCU", True, False, False),
    ("Corundum", "mineral", "SCU", True, False, True),
    ("Copper", "mineral", "SCU", True, False, True),
    ("Tin", "mineral", "SCU", True, False, True),
    ("Aluminium", "mineral", "SCU", True, False, True),
    ("Silicon", "mineral", "SCU", True, False, True),
    ("Inert Material", "mineral", "SCU", True, False, False),
    ("Janalite", "mineral", "SCU", True, False, True),
    ("Hadanite", "mineral", "SCU", True, False, False),
    ("Feynmaline", "mineral", "SCU", True, False, False),
    ("Aphorite", "mineral", "SCU", True, False, False),
    ("Dolivine", "mineral", "SCU", True, False, False),
    ("Glascosite", "mineral", "SCU", True, False, False),
    ("Carinite", "mineral", "SCU", True, False, False),
    ("Jaclium", "mineral", "SCU", True, False, False),
    ("Saldynium", "mineral", "SCU", True, False, False),

    # Salvage
    ("RMC", "salvage", "SCU", False, True, True),
    ("Scrap", "salvage", "SCU", False, True, True),
    ("Construction Materials", "salvage", "SCU", False, True, True),

    # Commerce (plus tard)
    ("Agricultural Supplies", "trade", "SCU", False, False, True),
    ("Ammonia", "trade", "SCU", False, False, True),
    ("Argon", "trade", "SCU", False, False, True),
    ("Astanite", "trade", "SCU", False, False, True),
    ("Atlasium", "trade", "SCU", False, False, True),
    ("Audio Visual Equipment", "trade", "SCU", False, False, True),
    ("Beradum", "trade", "SCU", False, False, True),
    ("Bioplastic", "trade", "SCU", False, False, True),
    ("Carbon", "trade", "SCU", False, False, True),
    ("Carbon-Silk", "trade", "SCU", False, False, True),
    ("Chlorine", "trade", "SCU", False, False, True),
    ("Cobalt", "trade", "SCU", False, False, True),
    ("Compboard", "trade", "SCU", False, False, True),
    ("Degnous Root", "trade", "SCU", False, False, True),
    ("Diamond", "trade", "SCU", False, False, True),
    ("Diamond Laminate", "trade", "SCU", False, False, True),
    ("Distilled Spirits", "trade", "SCU", False, False, True),
    ("Dymantium", "trade", "SCU", False, False, True),
    ("DynaFlex", "trade", "SCU", False, False, True),
    ("Fluorine", "trade", "SCU", False, False, True),
    ("Fresh Food", "trade", "SCU", False, False, True),
    ("Golden Medmon", "trade", "SCU", False, False, True),
    ("Heart of the Woods", "trade", "SCU", False, False, True),
    ("Helium", "trade", "SCU", False, False, True),
    ("Hydrogen", "trade", "SCU", False, False, True),
    ("Iodine", "trade", "SCU", False, False, True),
    ("Kopion Horn", "trade", "SCU", False, False, True),
    ("Luminalia Gift", "trade", "SCU", False, False, True),
    ("Marok Gem", "trade", "SCU", False, False, True),
    ("Medical Supplies", "trade", "SCU", False, False, True),
    ("Mercury", "trade", "SCU", False, False, True),
    ("Methane", "trade", "SCU", False, False, True),
    ("Nitrogen", "trade", "SCU", False, False, True),
    ("Omnapoxy", "trade", "SCU", False, False, True),
    ("Party Favors", "trade", "SCU", False, False, True),
    ("Potassium", "trade", "SCU", False, False, True),
    ("Pressurized Ice", "trade", "SCU", False, False, True),
    ("Processed Food", "trade", "SCU", False, False, True),
    ("Prota", "trade", "SCU", False, False, True),
    ("Ranta Dung", "trade", "SCU", False, False, True),
    ("Revenant Tree Pollen", "trade", "SCU", False, False, True),
    ("Ship Ammunition", "trade", "SCU", False, False, True),
    ("Souvenirs", "trade", "SCU", False, False, True),
    ("Steel", "trade", "SCU", False, False, True),
    ("Stims", "trade", "SCU", False, False, True),
    ("Sunset Berries", "trade", "SCU", False, False, True),
    ("Thermalfoam", "trade", "SCU", False, False, True),
    ("Waste", "trade", "SCU", False, False, True),
    ("Xa'Pyen", "trade", "SCU", False, False, True),
    ("Year Of The Pig Envelope", "trade", "SCU", False, False, True),
]

db = SessionLocal()

for name, cat, unit, mine, salv, trade in MATERIALS:
    if not db.query(Material).filter_by(name=name).first():
        db.add(Material(
            name=name,
            category=cat,
            unit=unit,
            is_mineable=mine,
            is_salvage=salv,
            is_trade_good=trade
        ))

db.commit()
db.close()

print("✅ Seed materials terminé")
