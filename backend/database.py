import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Format: postgresql://uzytkownik:haslo@host:port/database_name
DATABASE_URL: str  = str(os.getenv("DATABASE_URL"))


# Engine manages PostgreSQL connections
engine = create_engine(DATABASE_URL)

# Session class used for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class inherited by database models
BASE = declarative_base()


# Helper function (dependency) to open/close sessions in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
