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
    if not drawing.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Przesłany plik nie jest obrazem")

    try:
        img_bytes = await drawing.read()

        prediction, confidence = predict_digit(img_bytes) 

        print('===================')
        print(f'PREDYKCJA: {prediction}')
        print('===================\n')

        return {
            "prediction": prediction,
            "confidence": confidence 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")



@router.post("/save-img")
async def review_prediction( # nazwy zmiennych muszą zgadzać się z tym co jest przesyłane frontendu
    # 1. Odbieranie pliku
    drawing: UploadFile = File(...),
    
    # 2. Odbieranie pojedynczych pól z formularza
    prediction: int = Form(...),
    confidence: float = Form(...),
    correct_digit: int = Form(...),

    db: Session = Depends(get_db)
):
    if not drawing.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Plik nie jest obrazem")
    
    try:
        # Odczytanie obrazu
        img_bytes = await drawing.read()

        save_img(img_bytes=img_bytes, prediction=prediction, confidence=confidence, correct_digit=correct_digit, db=db)

        # Zwracamy odpowiedź do frontendu
        return {
            "status": "success",
            "message": "Dane poprawione przez użytkownika zostały zapisane."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")



@router.get("/retrain")
async def retrain(db: Session = Depends(get_db)):
    try:
        retrain_model(db=db)
        return {
            "status": "success",
            "message": "Model został przetrenowany."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")