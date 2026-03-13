from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from data.data import Base

class Reciept(Base):
    __tablename__ = 'reciepts'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer)
    items = Column(JSON)
    total_price = Column(Float)
    payment_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
