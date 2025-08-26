import os
from dotenv import load_dotenv

load_dotenv()    


class DevelopmentConfig(object):
    TESTING = False
    DEBUG = True
    
    # Database configuration
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_url = os.getenv('DB_URL')
    db_name = os.getenv('DB_NAME')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_url}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings for development
    SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP in development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'