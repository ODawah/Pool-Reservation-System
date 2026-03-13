from sqlalchemy import Column, Integer, String, Float, Boolean
from data.data import Base

class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer)
    clock_in_time = Column(String)  # Store as string for simplicity, or use DateTime type
    clock_out_time = Column(String)  # Store as string for simplicity, or use DateTime type
    today_cash = Column(Integer)  # Cash collected during the day