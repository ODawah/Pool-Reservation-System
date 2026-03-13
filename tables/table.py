from sqlalchemy import Column, Integer, String, Float, Boolean
from data.data import Base

class Table(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

class TableSessions(Base):
    __tablename__ = 'table_sessions'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer)
    start_time = Column(String)
    end_time = Column(String)
    total_price = Column(Float)