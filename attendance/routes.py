from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from data.data import SessionLocal
from attendance import attendance
import datetime

router = APIRouter(prefix="/attendance", tags=["attendance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_attendance(db: Session = Depends(get_db)):
    return db.query(attendance.Attendance).all()

#get today attendance records
@router.get("/today")
async def list_today_attendance(db: Session = Depends(get_db)):
    day_start = datetime.datetime.now().replace(hour=0, minute=0, second=0)
    return (
        db.query(attendance.Attendance)
        .filter(attendance.Attendance.clock_in_time >= day_start)
        .all()
    )

@router.post("/attend")
async def create_attendance(employee_id: int, db: Session = Depends(get_db)):
    attendance_record = attendance.Attendance(
        employee_id=employee_id,
        clock_in_time=datetime.datetime.now(),
    )
    db.add(attendance_record)
    db.commit()
    return {"message": "Attendance record created successfully"}

@router.put("/leave")
async def update_attendance(employee_id: int, db: Session = Depends(get_db)):
    # find the attendance record for the employee that has no clock_out_time and clockin_time is today
    day_start = datetime.datetime.now().replace(hour=0, minute=0, second=0)
    attendance_record = (
        db.query(attendance.Attendance)
        .filter(
            attendance.Attendance.employee_id == employee_id,
            attendance.Attendance.clock_out_time == None,
            attendance.Attendance.clock_in_time >= day_start,
        )
        .first()
    )
    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    attendance_record.clock_out_time = datetime.datetime.now()
    db.commit()
    return {"message": "Attendance record updated successfully"}
