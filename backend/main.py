# main.py
from dotenv import load_dotenv
load_dotenv(override=True)


from fastapi import FastAPI
from backend.database import engine, BASE

from backend.api.predict import router as predict_router
from fastapi.middleware.cors import CORSMiddleware

import backend.models

# Automatycznie tworzy tabele w bazie
BASE.metadata.create_all(bind=engine)

app = FastAPI()


# 2. Definiujemy listę adresów (origins), które mają mieć dostęp do naszego API
origins = [
    "http://localhost:5173",  # Domyślny adres dla projektów Vue (Vite) lub React
    "http://localhost:5174",  # Domyślny adres dla projektów Vue (Vite) lub React
    "http://localhost:3000",  # Alternatywny port, np. starsze konfiguracje React / Next.js
    "http://127.0.0.1:5173",  # Warto dodać również warianty z IP
]



# 3. Podłączamy CORSMiddleware do naszej aplikacji FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Zezwalaj na ruch tylko z tych adresów z listy wyżej
    allow_credentials=True,          # Zezwalaj na przesyłanie plików cookie / sesji / autoryzacji
    allow_methods=["*"],             # Zezwalaj na wszystkie metody HTTP (GET, POST, PUT, DELETE itp.)
    allow_headers=["*"],             # Zezwalaj na wszystkie nagłówki (np. Content-Type, Authorization)
)


# Opcjonalnie możemy dodać prefix, np. prefix="/api"
app.include_router(predict_router)