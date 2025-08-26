import os
from dotenv import load_dotenv

load_dotenv()    


class ProductionConfig(object):
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database configuration
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_url = os.getenv('DB_URL')
    db_name = os.getenv('DB_NAME')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_url}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 2000,      # MAX 2000 pool size
        "pool_recycle": 1800,   # Close connections after 30 mins
        "pool_timeout": 15,     # Wait 15 seconds before failing
        "max_overflow": 5       # Permits 5 extra connections
    }
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True   # Require HTTPS for cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'  # Strict CSRF protection
    
    # CSRF Protection settings
    CSRF_TOKEN_TIMEOUT = 1800  # 30 minutes in seconds
    CSRF_SECRET_KEY = os.getenv('SECRET_KEY')