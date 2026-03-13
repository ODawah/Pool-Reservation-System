# tables/routes.py
from http.client import HTTPException
from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data.data import SessionLocal
from tables.table import Table

router = APIRouter(prefix="/tables", tags=["tables"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_tables(db: Session = Depends(get_db)):
    return db.query(Table).all()

# update table price
@router.put("/{table_id}")
async def update_table_price(table_id: int, price: float, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    #convert price to per minute
    table.price = price / 60
    db.commit()
    return {"message": "Table price updated successfully"}