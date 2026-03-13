from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime

from data.data import Base

class Revenue(Base):
    __tablename__ = 'revenues'

    id = Column(Integer, primary_key=True)
    source = Column(String)
    amount = Column(Float)
    date = Column(DateTime)  