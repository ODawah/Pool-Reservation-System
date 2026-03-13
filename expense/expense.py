from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from data.data import Base

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime)  # Store as string for simplicity, or use DateTime type