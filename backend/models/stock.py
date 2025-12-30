from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Integer, nullable=False)
    source = Column(String)
