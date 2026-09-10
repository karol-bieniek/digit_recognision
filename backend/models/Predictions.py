from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from backend.database import BASE

class Predictions(BASE):
    __tablename__ = "predictions"
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key=True, index=True)
    
    # Prediction and correction data
    predicted_digit = Column(Integer, nullable=False) # What the model predicted
    correct_digit = Column(Integer, nullable=False)   # True digit (user label)
    confidence = Column(Float, nullable=True)         # Model confidence (e.g. 0.87)
    is_correct = Column(Boolean, nullable=False)      # 1 if prediction is correct, 0 if incorrect
    
    # File location (instead of BLOB)
    image_path = Column(String(512), nullable=False)  # np. "s3://my-bucket/digits/2026-08-12_abc123.png"
    
    # MLOps metadata
    model_version = Column(String(50), nullable=False) # np. "mnist_v1.2.0"
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Event timestamp