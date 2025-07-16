import os
from dotenv import load_dotenv
from minio import Minio
from urllib.parse import urlparse
load_dotenv()

def getMinioClient():
    return Minio(
        endpoint=f"{os.getenv('S3_HOST')}:{os.getenv('S3_PORT')}",
        secure=(os.getenv('ENV_MODE') == "production"),
        access_key=os.getenv('S3_ACCESS_KEY'),
        secret_key=os.getenv('S3_SECRET_KEY'),
    )

def getMinioClientExternal():
    s3LiveBaseUrl = os.getenv('S3_LIVE_BASE_URL').rstrip('/')
    parsed_base = urlparse(s3LiveBaseUrl)
    external_host = parsed_base.hostname
    external_port = parsed_base.port if parsed_base.port else (443 if parsed_base.scheme == 'https' else 80)

    return Minio(
        endpoint=f"{external_host}:{external_port}",
        access_key=os.getenv('S3_ACCESS_KEY'),
        secret_key=os.getenv('S3_SECRET_KEY'),
        secure=(parsed_base.scheme == 'https'),
    )