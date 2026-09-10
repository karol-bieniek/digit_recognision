from minio import Minio
import io
from PIL import Image, ImageOps
import torchvision.transforms as transforms
import os


# Konfiguracja klienta MinIO
minio_client = Minio(
    os.getenv("MINIO_URL"),          # Adres Twojego serwera MinIO
    access_key=os.getenv("MINIO_LOGIN"),   # Twój login (Access Key)
    secret_key=os.getenv("MINIO_PASSWORD"),   # Twoje hasło (Secret Key)
    secure=False               # False, jeśli testujesz lokalnie bez HTTPS
)

BUCKET_NAME = "drawings"

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)




def get_image(bucket_name: str, object_name: str):
    try:
        # 2. Pobranie obiektu (obrazka) z MinIO
        response = minio_client.get_object(bucket_name, object_name)
        
        # 3. Wczytanie surowych bajtów obrazu do pamięci
        image_bytes = response.read()
        
        # 4. Konwersja bajtów na obiekt obrazu (PIL Image)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Opcjonalnie: upewnij się, że obraz to skala szarości (dla MNIST)
        image = image.convert("L")

        image = ImageOps.invert(image)  # Inwersja kolorów

        return image 

    except Exception as e:
        print(f"Błąd podczas pobierania obrazu z MinIO: {e}")
        return None

    finally:
        # 6. Bardzo ważne: zwolnienie połączenia!
        # Zapobiega zablokowaniu serwera przy dużej liczbie zapytań
        if 'response' in locals():
            response.close()
            response.release_conn()