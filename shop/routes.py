from http.client import HTTPException
from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data.data import SessionLocal
from shop.shop import ShopItem

router = APIRouter(prefix="/shop", tags=["shop"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_shop_items(db: Session = Depends(get_db)):
    return db.query(ShopItem).all()

@router.post("/")
async def create_shop_item(name: str, price: float, quantity: int, db: Session = Depends(get_db)):
    item = ShopItem(name=name, price=price, quantity=quantity)
    db.add(item)
    db.commit()
    return {"message": "Item created successfully"}

## update shop item price
@router.put("/{item_id}/price")
async def update_shop_item_price(item_id: int, price: float, db: Session = Depends(get_db)):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.price = price
    db.commit()
    return {"message": "Item price updated successfully"}

## update shop item quantity
@router.put("/{item_id}/quantity/add")
async def update_shop_item_quantity(item_id: int, quantity: int, db: Session = Depends(get_db)):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity += quantity
    db.commit()
    return {"message": "Item quantity updated successfully"}


@router.put("/{item_id}/quantity/subtract")
async def update_shop_item_quantity(item_id: int, quantity: int, db: Session = Depends(get_db)):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity -= quantity
    db.commit()
    return {"message": "Item quantity updated successfully"}

@router.delete("/{item_id}")
async def delete_shop_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

