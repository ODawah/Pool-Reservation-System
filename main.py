from data.data import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from tables.routes import router as tables_router
from shop.routes import router as shop_router
from employee.routes import router as employees_router
from attendance.routes import router as attendance_router
from revenue.routes import router as revenue_router
from reciept.routes import router as reciepts_router
from expense.routes import router as expenses_router

Base.metadata.create_all(bind=engine)


def _ensure_schema():
    with engine.begin() as conn:
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(reciepts)"))}
        if "payment_type" not in columns:
            conn.execute(text("ALTER TABLE reciepts ADD COLUMN payment_type VARCHAR"))


_ensure_schema()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
app.include_router(tables_router)
app.include_router(shop_router)
app.include_router(employees_router)
app.include_router(attendance_router)
app.include_router(revenue_router)
app.include_router(reciepts_router)
app.include_router(expenses_router)
