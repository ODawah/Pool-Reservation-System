# from sqlalchemy.orm import Session
# from data.data import engine
# from tables.table import Table

# def seed_tables():
#     session = Session(bind=engine)

#     tables_data = [
#         {"name": "Pool 1", "price": 3 / 60 },
#         {"name": "Pool 2", "price": 3 / 60},
#         {"name": "Pool 3", "price": 3 / 60},
#         {"name": "Pool 4", "price": 3 / 60},
#         {"name": "Carrom 1", "price": 2 / 60},
#         {"name": "PS Room", "price": 10 / 60},
#     ]

#     for data in tables_data:
#         exists = session.query(Table).filter_by(name=data["name"]).first()
#         if not exists:
#             session.add(Table(**data))

#     session.commit()
#     session.close()

#     print("✅ Tables seeded successfully")

# if __name__ == "__main__":
#     seed_tables()
from sqlalchemy.orm import Session
from data.data import engine
from shop.shop import ShopItem

def seed_shop_items():
    session = Session(bind=engine)

    items = [
        "cheetos",
        "flamnco",
        "chipsy",
        "doritos",
        "jaguar",
        "Tiger",
        "Spuds",
        "popcorn",
        "biskrem",
        "freska",
        "oreo",
        "Tea",
        "small water",
        "large water",
        "nescafe",
        "turkish coffee",
        "turkish coffee double",
        "espresso",
        "twinkies",
        "hohos",
        "pepsi",
        "v cola",
        "mountain view",
        "sprite",
        "mirinda",
    ]

    for name in items:
        exists = session.query(ShopItem).filter_by(name=name).first()
        if exists:
            exists.quantity = 10
            continue
        session.add(
            ShopItem(
                name=name,
                price=10,
                quantity=10,
            )
        )

    session.commit()
    session.close()

    print("✅ Shop items seeded successfully")

if __name__ == "__main__":
    seed_shop_items()
