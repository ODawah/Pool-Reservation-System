import os
import libsql_experimental as libsql
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

TURSO_URL = os.environ["TURSO_DATABASE_URL"]
TURSO_TOKEN = os.environ["TURSO_AUTH_TOKEN"]

def create_connection():
    return libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)

engine = create_engine(
    "sqlite+libsql://",
    creator=create_connection,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
