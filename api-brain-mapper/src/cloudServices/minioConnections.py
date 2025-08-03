import os
from dotenv import load_dotenv
from minio import Minio
from urllib.parse import urlparse
load_dotenv()


def getMinioClient():
    s3LiveBaseUrl = os.getenv('S3_LIVE_BASE_URL').rstrip('/')  # Assuming the URL is in the format 'https://example.com/bucket'
    parsed_base = urlparse(s3LiveBaseUrl)  # Parse the URL to get only the host and port
    host = parsed_base.hostname
    port = parsed_base.port if parsed_base.port else (443 if parsed_base.scheme == 'https' else 80)  # Make sure there's a port otherwise set defaults
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    return Minio(
        endpoint=f"{host}:{port}",
        access_key=access_key,
        secret_key=secret_key,
        secure=(os.getenv('ENV_MODE') == "production"),
    )