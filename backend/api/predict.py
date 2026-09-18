from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import io
from PIL import Image 

from backend.database import get_db
from backend.models.Predictions import Predictions


from ..services.digit_recognision import predict_digit, save_img, retrain_model

router = APIRouter()

@router.post("/predict")
async def predict(drawing: UploadFile = File(...)):
    if not drawing.content_type or not drawing.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    try:
        img_bytes = await drawing.read()

        prediction, confidence = predict_digit(img_bytes) 

        return {
            "prediction": prediction,
            "confidence": confidence 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



@router.post("/save-img")
async def review_prediction( # variable names must match what frontend sends
    drawing: UploadFile = File(...),
    
    prediction: int = Form(...),
    confidence: float = Form(...),
    correct_digit: int = Form(...),

    db: Session = Depends(get_db)
):
    if not drawing.content_type or not drawing.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    try:
        img_bytes = await drawing.read()

        save_img(img_bytes=img_bytes, prediction=prediction, confidence=confidence, correct_digit=correct_digit, db=db)

        return {
            "status": "success",
            "message": "User-corrected data has been saved."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



@router.get("/retrain")
async def retrain(db: Session = Depends(get_db)):
    try:
        retrain_model(db=db)
        return {
            "status": "success",
            "message": "Model has been retrained."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")