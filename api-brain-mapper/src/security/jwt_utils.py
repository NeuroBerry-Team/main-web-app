import os
import jwt
from datetime import datetime, timedelta, timezone


def encode_auth_jwt(uid, expires_in=1440):  # Default 24 hours in minutes
    try:
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(minutes=expires_in),
            'iat': datetime.now(timezone.utc),
            'uid': uid
        }

        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            raise Exception('SECRET_KEY environment variable not set')

        return jwt.encode(
            payload,
            secret_key,
            algorithm='HS256'
        )
    except Exception as e:
        raise e


def decode_auth_jwt(auth_jwt):
    try:
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            raise Exception('SECRET_KEY environment variable not set')
            
        payload = jwt.decode(
            auth_jwt,
            secret_key,
            algorithms=['HS256']
        )

        return payload['uid']

    except jwt.ExpiredSignatureError:
        raise Exception('expired_token')
    except jwt.InvalidTokenError:
        raise Exception('invalid_token')
