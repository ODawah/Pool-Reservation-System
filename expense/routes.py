from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from data.data import SessionLocal
from expense.expense import Expense

router = APIRouter(prefix="/expenses", tags=["expenses"])


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    date: Optional[datetime] = None


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None


class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.id.desc()).all()


@router.post("/", response_model=ExpenseResponse, status_code=201)
async def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(
        description=payload.description,
        amount=payload.amount,
        date=payload.date or datetime.now(),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if payload.description is not None:
        expense.description = payload.description
    if payload.amount is not None:
        expense.amount = payload.amount
    if payload.date is not None:
        expense.date = payload.date

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}
