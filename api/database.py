from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database.db"
READONLY_DATABASE_URL = "sqlite:///./database.db?mode=ro"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

readonly_engine = create_engine(
    READONLY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadonlySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=readonly_engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_readonly_db():
    db = ReadonlySessionLocal()
    try:
        yield db
    finally:
        db.close()