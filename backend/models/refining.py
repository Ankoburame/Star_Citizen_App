from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class RefiningJob(Base):
    __tablename__ = "refining_jobs"

    id = Column(Integer, primary_key=True)
    input_material_id = Column(Integer, ForeignKey("materials.id"))
    output_material_id = Column(Integer, ForeignKey("materials.id"))

    input_quantity = Column(Integer)
    output_quantity = Column(Integer)

    status = Column(String)  # ACTIVE | DONE

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer)

    input_material = relationship(
        "Material",
        foreign_keys=[input_material_id],
    )

    output_material = relationship(
        "Material",
        foreign_keys=[output_material_id],
    )
