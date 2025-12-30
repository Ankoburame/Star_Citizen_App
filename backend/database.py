from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://sc_user:qsp1MhWM9S4QWHvaruNv@localhost:5432/starcitizen_prod"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()
print("database.py chargé, engine =", engine)
