from minio import Minio
import io
from PIL import Image, ImageOps
import torchvision.transforms as transforms
import os


# MinIO client configuration
minio_client = Minio(
    os.getenv("MINIO_URL"),          # Address of your MinIO server
    access_key=os.getenv("MINIO_LOGIN"),   # Your login (Access Key)
    secret_key=os.getenv("MINIO_PASSWORD"),   # Your password (Secret Key)
    secure=False               # False when testing locally without HTTPS
)

BUCKET_NAME = "drawings"

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)




def get_image(bucket_name: str, object_name: str):
    try:
        # 2. Download object (image) from MinIO
        response = minio_client.get_object(bucket_name, object_name)
        
        # 3. Read raw image bytes into memory
        image_bytes = response.read()
        
        # 4. Convert bytes to image object (PIL Image)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Optional: ensure image is grayscale (for MNIST)
        image = image.convert("L")

        image = ImageOps.invert(image)  # Invert colors

        return image 

    except Exception as e:
        print(f"Error while downloading image from MinIO: {e}")
        return None

    finally:
        # 6. Very important: release connection!
        # Prevents server blocking under high request volume
        if 'response' in locals():
            response.close()
            response.release_conn()