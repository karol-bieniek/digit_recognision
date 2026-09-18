from typing import cast

import torch
import io
import uuid
import random


from sqlalchemy.orm import Session

from backend.models.Predictions import Predictions
from backend.model_training.NeuralNetwork import NeuralNetwork, INPUT_IMG_SIZE, device, train, test 

from PIL import Image

from torchvision import transforms
from torch.utils.data import TensorDataset, ConcatDataset, DataLoader
from torch import Tensor, nn


from sqlalchemy.exc import SQLAlchemyError

from minio.error import S3Error
from backend.storage import minio_client, BUCKET_NAME, get_image




NN_MODEL = NeuralNetwork().to(device)
# NN_MODEL.load_state_dict(torch.load("backend/model.pth", weights_only=True))
NN_MODEL.load_state_dict(torch.load("backend/model.pth", map_location=torch.device('cpu'), weights_only=True))

preprocess = transforms.Compose([
    transforms.Grayscale(num_output_channels=1), # Convert to 1 channel (black and white)
    transforms.Resize((28, 28)),                 # Force size to 28x28
    transforms.ToTensor(),                       # Convert to tensor with values in [0.0, 1.0]
]) 



def predict_digit(img_bytes: bytes) -> tuple[int, float]:
    
    with Image.open(io.BytesIO(img_bytes)) as img:
        # Convert RGBA to RGB with forced white background
        if img.mode == 'RGBA':
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3]) # Apply using alpha mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        img_tensor = cast(Tensor, preprocess(img))

        img_tensor = 1.0 - img_tensor

        img_tensor = img_tensor.unsqueeze(0) # add batch dimension (1 batch in this case)
        img_tensor = img_tensor.to(device)   # model runs on selected accelerator/cpu


        NN_MODEL.eval()
        with torch.no_grad():
            logits = NN_MODEL(img_tensor)
            probabilities = torch.softmax(logits, dim=1)
            prediction = int(torch.argmax(probabilities, dim=1).item())
            confidence = float(probabilities[0][prediction].item())    # index 0 because torch output is batched


        confidence = round(confidence*100, 2)

    return (prediction, confidence)




def save_img(img_bytes: bytes, prediction: int, confidence: float, correct_digit: int, db: Session):
    user_prediction = Predictions()
    user_prediction.predicted_digit = prediction
    user_prediction.confidence = confidence
    user_prediction.correct_digit = correct_digit
    user_prediction.model_version = "conv_nn_1"
    user_prediction.is_correct = prediction == correct_digit

    drawing_name = f"{uuid.uuid4()}.png"
    img_stream = io.BytesIO(img_bytes)
    img_size = len(img_bytes)

    try:
        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=drawing_name,
            data=img_stream,
            length=img_size,
            content_type="image/png" 
        )

        user_prediction.image_path = drawing_name
        db.add(user_prediction)
        db.commit()
        
    except S3Error as e:
        print(f"MinIO write error: {e}")
        raise

    except SQLAlchemyError as e:
        db.rollback() 
        minio_client.remove_object(bucket_name=BUCKET_NAME, object_name=drawing_name)
        print(f"Database error (SQLAlchemy): {e}")
        raise



def retrain_model(db: Session):
    correct_predictions = db.query(Predictions).filter(Predictions.is_correct == True).all()
    incorrect_predictions = db.query(Predictions).filter(Predictions.is_correct == False).all()

    # Set ratio: 4 correct predictions for 1 incorrect one
    num_incorrect = len(incorrect_predictions) # 
    num_correct_needed = num_incorrect * 4     # 4:1 ratio (correct:incorrect)

    if len(correct_predictions) < num_correct_needed:
        print(f"Warning: Not enough correct predictions. Using all available ({len(correct_predictions)}).")
        num_correct_needed = len(correct_predictions)

    sampled_correct = random.sample(correct_predictions, num_correct_needed)
    # Prepare data for model training
    X_correct = []
    y_correct = []

    X_incorrect = []
    y_incorrect = []

    for pred in sampled_correct:
        img = get_image(BUCKET_NAME, pred.image_path)
        if img is not None:
            img_tensor = preprocess(img)
            X_correct.append(img_tensor)
            y_correct.append(torch.tensor(pred.correct_digit))


    for pred in incorrect_predictions:
        img = get_image(BUCKET_NAME, pred.image_path)
        if img is not None:
            img_tensor = preprocess(img)
            X_incorrect.append(img_tensor)
            y_incorrect.append(torch.tensor(pred.correct_digit))


    if len(X_correct) == 0 or len(X_incorrect) == 0:
        print("Not enough data for training. Retraining process was stopped.")
        return

    dataset_correct = TensorDataset(torch.stack(X_correct), torch.stack(y_correct))
    dataset_incorrect = TensorDataset(torch.stack(X_incorrect), torch.stack(y_incorrect))

    mixed_dataset = ConcatDataset([dataset_correct, dataset_incorrect])


    train_dataloader = DataLoader(mixed_dataset, batch_size=64, shuffle=True)
    # test_dataloader = DataLoader(test_dataset, batch_size=64, shuffle=True)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(NN_MODEL.parameters(), lr=0.001)


    train(dataloader=train_dataloader, model=NN_MODEL, loss_fn=loss_fn, optimizer=optimizer)


    torch.save(NN_MODEL.state_dict(), "backend/model.pth")
    print("Saved PyTorch Model State to backend/model.pth")