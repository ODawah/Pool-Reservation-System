from sqlalchemy import Column, Integer, String, Float, Boolean
from data.data import Base

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    salary = Column(Float)