from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Format: postgresql://uzytkownik:haslo@host:port/nazwa_bazy
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine to silnik, który zarządza połączeniami z PostgreSQL
engine = create_engine(DATABASE_URL)

# Klasa sesji - za jej pomocą będziemy wykonywać operacje na bazie
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Klasa bazowa, po której będą dziedziczyć nasze modele bazodanowe
BASE = declarative_base()

# Funkcja pomocnicza (tzw. Dependency) do otwierania/zamykania sesji w endpointach
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()