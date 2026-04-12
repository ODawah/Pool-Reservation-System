import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from data.data import SessionLocal
from reciept.reciept import Reciept

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo

router = APIRouter(prefix="/reciept", tags=["reciepts"])
RECIEPT_TIMEZONE = ZoneInfo("Africa/Cairo")


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


def _serialize_reciept_row(row: Any) -> Dict[str, Any]:
    parsed_items: Dict[str, Any] = {}
    if isinstance(row, dict):
        raw_items = row["items"]
        reciept_id = row["id"]
        table_id = row["table_id"]
        total_price = row["total_price"]
        payment_type = row["payment_type"]
        timestamp = row["timestamp"]
    else:
        raw_items = row.items
        reciept_id = row.id
        table_id = row.table_id
        total_price = row.total_price
        payment_type = row.payment_type
        timestamp = row.timestamp

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

    return {
        "id": reciept_id,
        "table_id": table_id,
        "items": parsed_items,
        "total_price": total_price,
        "payment_type": payment_type,
        "timestamp": timestamp,
    }


def _normalize_reciept_timestamp(value: Optional[datetime]) -> datetime:
    if value is None:
        return datetime.now(RECIEPT_TIMEZONE).replace(tzinfo=None)

    if value.tzinfo is None:
        return value

    return value.astimezone(RECIEPT_TIMEZONE).replace(tzinfo=None)


@router.get("/", response_model=List[RecieptResponse])
async def list_reciepts(db: Session = Depends(get_db)):
    rows = db.query(Reciept).order_by(Reciept.timestamp.desc(), Reciept.id.desc()).all()

    return [_serialize_reciept_row(row) for row in rows]


@router.get("/by-date", response_model=List[RecieptResponse])
async def list_reciepts_by_date(
    date_value: str = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    try:
        selected_date = date.fromisoformat(date_value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format") from exc

    start_of_day = datetime.combine(selected_date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    rows = (
        db.query(Reciept)
        .filter(Reciept.timestamp >= start_of_day, Reciept.timestamp < end_of_day)
        .order_by(Reciept.timestamp.desc(), Reciept.id.desc())
        .all()
    )

    return [_serialize_reciept_row(row) for row in rows]


@router.post("/", response_model=RecieptResponse, status_code=201)
async def create_reciept(payload: RecieptCreate, db: Session = Depends(get_db)):
    reciept = Reciept(
        table_id=payload.table_id,
        items=payload.items,
        total_price=payload.total_price,
        payment_type=payload.payment_type,
        timestamp=_normalize_reciept_timestamp(payload.timestamp),
    )
    db.add(reciept)
    db.commit()
    db.refresh(reciept)
    return reciept
