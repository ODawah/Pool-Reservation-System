from sqlalchemy import Column, Integer, String, Float, Boolean
from data.data import Base

class ShopItem(Base):
    __tablename__ = 'shop_items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    