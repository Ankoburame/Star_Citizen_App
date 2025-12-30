# services/refining_service.py

from datetime import datetime
from sqlalchemy.orm import Session

from models.refining import RefiningJob
from models.stock_event import StockEvent


def start_refining(
    input_material_id: int,
    output_material_id: int,
    input_quantity: int,
    output_quantity: int,
    duration_minutes: int,
    db: Session,
):
    # 1️⃣ Création du job
    job = RefiningJob(
        input_material_id=input_material_id,
        output_material_id=output_material_id,
        input_quantity=input_quantity,
        output_quantity=output_quantity,
        duration_minutes=duration_minutes,
        started_at=datetime.utcnow(),
        status="RUNNING",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # 2️⃣ Consommation du brut (NEUTRE financièrement)
    consume_event = StockEvent(
        material_id=input_material_id,
        quantity=-input_quantity,
        unit_price=0.0,
        total_value=0.0,
        event_type="REFINING_CONSUME",
        reference_type="REFINING",
        reference_id=job.id,
    )

    db.add(consume_event)
    db.commit()

    return job.id
