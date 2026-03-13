from http.client import HTTPException
from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data.data import SessionLocal
from employee.employee import Employee

router = APIRouter(prefix="/employee", tags=["employee"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@router.post("/")
async def create_employee(name: str, role: str, salary: float, db: Session = Depends(get_db)):
    employee = Employee(name=name, role=role, salary=salary)
    db.add(employee)
    db.commit()
    return {"message": "Employee created successfully"}

@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}