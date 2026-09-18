import io
from unittest import mock
import pytest
from PIL import Image, UnidentifiedImageError
import torch

from backend.models.Predictions import Predictions
from backend.services.digit_recognision import predict_digit, save_img, retrain_model

from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from minio.error import S3Error
# TEST UTILITIES

PATCH_BASE = "backend.services.digit_recognision"

def generate_image_bytes(mode: str, size=(100, 100)) -> bytes:
    if mode == "RGBA":
        img = Image.new(mode, size, (0, 0, 0, 0))
    elif mode == "RGB":
        img = Image.new(mode, size, (255, 0, 0))
    else:
        img = Image.new(mode, size, 128)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


##############
# TEST CASES #
##############


# Test cases for predict_digit function
def test_predict_digit_handles_rgba():
    img_bytes = generate_image_bytes("RGBA")
    prediction, confidence = predict_digit(img_bytes)
    
    assert isinstance(prediction, int)
    assert isinstance(confidence, float)
    assert 0 <= prediction <= 9
    assert 0.0 <= confidence <= 100.0



def test_predict_digit_handles_rgb():
    img_bytes = generate_image_bytes("RGB")
    prediction, confidence = predict_digit(img_bytes)
    
    assert isinstance(prediction, int)
    assert isinstance(confidence, float)
    assert 0 <= prediction <= 9



def test_predict_digit_handles_grayscale():
    img_bytes = generate_image_bytes("L")
    prediction, confidence = predict_digit(img_bytes)
    
    assert isinstance(prediction, int)
    assert isinstance(confidence, float)


def test_predict_digit_rejects_invalid_bytes():
    invalid_bytes = b"not a valid image"
    
    with pytest.raises(UnidentifiedImageError):
        predict_digit(invalid_bytes)



# Test cases for save_img function
@patch(f"{PATCH_BASE}.minio_client")
def test_save_img_success(mock_minio_client):
    mock_db = MagicMock()
    img_bytes = b"fake_image_data"
    
    save_img(
        img_bytes=img_bytes,
        prediction=5,
        confidence=95.5,
        correct_digit=5,
        db=mock_db
    )
    
    mock_minio_client.put_object.assert_called_once()
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

    added_prediction = mock_db.add.call_args[0][0]
    assert added_prediction.predicted_digit == 5
    assert added_prediction.is_correct is True



@patch(f"{PATCH_BASE}.minio_client")
def test_save_img_minio_failure(mock_minio_client):
    mock_db = MagicMock()
    
    mock_error = S3Error(
        code="InternalError", message="MinIO is down", 
        resource="bucket", request_id="1", host_id="2", response=MagicMock()
    )
    mock_minio_client.put_object.side_effect = mock_error
    
    with pytest.raises(S3Error):
        save_img(b"fake", 5, 95.5, 5, mock_db)
        
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_minio_client.remove_object.assert_not_called()


@patch(f"{PATCH_BASE}.minio_client")
def test_save_img_database_failure(mock_minio_client):
    mock_db = MagicMock()
    
    mock_db.commit.side_effect = SQLAlchemyError("DB Connection Lost")
    
    with pytest.raises(SQLAlchemyError):
        save_img(b"fake", 3, 50.0, 7, mock_db)
        
    mock_db.rollback.assert_called_once()
    mock_minio_client.remove_object.assert_called_once()


# Test cases for retrain_model function

@patch(f"{PATCH_BASE}.torch.save")
@patch(f"{PATCH_BASE}.train")
@patch(f"{PATCH_BASE}.get_image")
def test_retrain_model_not_enough_data(mock_get_image, mock_train, mock_save):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    retrain_model(mock_db)
    
    mock_train.assert_not_called()
    mock_save.assert_not_called()



@patch(f"{PATCH_BASE}.torch.save")
@patch(f"{PATCH_BASE}.train")
@patch(f"{PATCH_BASE}.preprocess")
@patch(f"{PATCH_BASE}.get_image")
def test_retrain_model_ratio_and_execution(mock_get_image, mock_preprocess, mock_train, mock_save):
    mock_db = MagicMock()
    
    incorrect_pred = Predictions(image_path="err.png", correct_digit=3, is_correct=False)
    correct_preds = [Predictions(image_path=f"ok_{i}.png", correct_digit=7, is_correct=True) for i in range(10)]
    
    mock_query = MagicMock()
    mock_query.filter.return_value.all.side_effect = [correct_preds, [incorrect_pred]] # First call returns correct predictions, second call returns incorrect prediction
    mock_db.query.return_value = mock_query
    
    mock_get_image.return_value = b"fake_img"
    
    mock_preprocess.return_value = torch.zeros((1, 28, 28))
    
    retrain_model(mock_db)
    

    assert mock_get_image.call_count == 5 # 1 incorrect + 4 correct images - ratio 4:1
    
    mock_train.assert_called_once()
    
    
    mock_save.assert_called_once_with(mock.ANY, "backend/model.pth")