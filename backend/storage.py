from minio import Minio
import io
from PIL import Image, ImageOps
import torchvision.transforms as transforms
import os


# MinIO client configuration
minio_client = Minio(
    os.getenv("MINIO_URL"),          # Address of your MinIO server # type: ignore
    access_key=os.getenv("MINIO_LOGIN"),   # Your login (Access Key)
    secret_key=os.getenv("MINIO_PASSWORD"),   # Your password (Secret Key)
    secure=False               # False when testing locally without HTTPS
)

BUCKET_NAME = "drawings"





def get_image(bucket_name: str, object_name: str):
    try:
        with minio_client.get_object(bucket_name, object_name) as response:
            image_bytes = response.read()

        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("L")
        return ImageOps.invert(image)

    except Exception as e:
        print(f"Error while downloading image from MinIO: {e}")
        return None