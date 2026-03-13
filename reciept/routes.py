import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
from data.data import SessionLocal
from reciept.reciept import Reciept

router = APIRouter(prefix="/reciept", tags=["reciepts"])


class RecieptCreate(BaseModel):
    table_id: int
    items: Dict[str, Any]
    total_price: float
    payment_type: str
    timestamp: Optional[datetime] = None


class RecieptResponse(BaseModel):
    id: int
    table_id: int
    items: Dict[str, Any]
    total_price: float
    payment_type: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[RecieptResponse])
async def list_reciepts(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            "SELECT id, table_id, items, total_price, payment_type, timestamp "
            "FROM reciepts ORDER BY id DESC"
        )
    ).mappings().all()

    reciepts: List[Dict[str, Any]] = []
    for row in rows:
        parsed_items: Dict[str, Any] = {}
        raw_items = row["items"]

        if isinstance(raw_items, dict):
            parsed_items = raw_items
        elif isinstance(raw_items, str):
            try:
                loaded = json.loads(raw_items)
                if isinstance(loaded, dict):
                    parsed_items = loaded
                else:
                    parsed_items = {"value": loaded}
            except (json.JSONDecodeError, TypeError):
                parsed_items = {"legacy_raw": raw_items}

        reciepts.append(
            {
                "id": row["id"],
                "table_id": row["table_id"],
                "items": parsed_items,
                "total_price": row["total_price"],
                "payment_type": row["payment_type"],
                "timestamp": row["timestamp"],
            }
        )

    return reciepts


@router.post("/", response_model=RecieptResponse, status_code=201)
async def create_reciept(payload: RecieptCreate, db: Session = Depends(get_db)):
    reciept = Reciept(
        table_id=payload.table_id,
        items=payload.items,
        total_price=payload.total_price,
        payment_type=payload.payment_type,
        timestamp=payload.timestamp or datetime.now(),
    )
    db.add(reciept)
    db.commit()
    db.refresh(reciept)
    return reciept
