from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from backend.database import BASE

class Predictions(BASE):
    __tablename__ = "predictions"
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key=True, index=True)
    
    # Dane o predykcji i poprawce
    predicted_digit = Column(Integer, nullable=False) # Co model wytypował
    correct_digit = Column(Integer, nullable=False)   # Prawdziwa cyfra (etykieta użytkownika)
    confidence = Column(Float, nullable=True)         # Pewność modelu (np. 0.87)
    is_correct = Column(Boolean, nullable=False)      # 1 jeśli poprawna predykcja, 0 jeśli błędna
    
    # Lokalizacja pliku (zamiast BLOB)
    image_path = Column(String(512), nullable=False)  # np. "s3://my-bucket/digits/2026-08-12_abc123.png"
    
    # Metadane MLOps
    model_version = Column(String(50), nullable=False) # np. "mnist_v1.2.0"
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Data zdarzenia