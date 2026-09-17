from dotenv import load_dotenv
load_dotenv(override=True)


from fastapi import FastAPI
from backend.database import engine, BASE
from contextlib import asynccontextmanager

from backend.api.predict import router as predict_router
from fastapi.middleware.cors import CORSMiddleware


# For creating
import backend.models
from backend.storage import minio_client, BUCKET_NAME

# Automatically create database tables
BASE.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
    yield


app = FastAPI(lifespan=lifespan)


# 2. Define list of origins allowed to access our API
origins = [
    "http://localhost:5173",  # Default address for Vue (Vite) or React projects
    "http://localhost:5174",  # Default address for Vue (Vite) or React projects
    "http://localhost:3000",  # Alternative port (e.g., older React / Next.js setups)
    "http://127.0.0.1:5173",  # Include IP-based variant as well
]



# 3. Attach CORSMiddleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allow traffic only from the origins listed above
    allow_credentials=True,          # Allow cookies / session / auth data
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],             # Allow all headers (e.g., Content-Type, Authorization)
)


app.include_router(predict_router)