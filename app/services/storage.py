import aiofiles
from minio import Minio
from minio.error import S3Error
import os
import io
from typing import Optional

# Налаштування мініо (або S3)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "reading-audio")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Ініціалізуємо клієнт
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# Створюємо bucket якщо не існує
def ensure_bucket():
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
    except S3Error as e:
        print(f"Failed to create bucket: {e}")

ensure_bucket()

async def upload_audio(file, file_key: str) -> str:
    """Завантажує аудіо-файл в storage і повертає URL"""
    
    # Читаємо файл
    content = await file.read()
    file_size = len(content)
    
    # Завантажуємо в мініо
    try:
        client.put_object(
            MINIO_BUCKET,
            file_key,
            io.BytesIO(content),
            file_size,
            content_type=file.content_type or "audio/webm"
        )
        
        # Формуємо публічний URL
        # Для мініо: http://localhost:9000/bucket/file_key
        # Для S3: https://bucket.s3.region.amazonaws.com/file_key
        url = f"http://localhost:9000/{MINIO_BUCKET}/{file_key}"
        return url
    except S3Error as e:
        raise Exception(f"Failed to upload to storage: {e}")