import os
from datetime import timedelta

class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLAlchemy Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///wine_recommender.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Application Settings
    DEBUG = False
    TESTING = False

    # Wine Recommendation Settings
    RECOMMENDATION_LIMIT = 10
    SIMILARITY_THRESHOLD = 0.7

    # File Upload Settings
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = 'epiphanywanjira@gmail.com'

    # Elasticsearch Configuration
    ELASTICSEARCH_HOST = 'http://localhost:9200'
    ELASTICSEARCH_WINE_INDEX = 'wine_discovery'
    # Caching Configuration
    CACHE_TYPE = 'redis'  # or 'filesystem' if Redis is not available
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    
    # Fallback to in-memory caching if Redis is not available
    CACHE_FALLBACK = 'simple'
    
    # Cache timeout settings
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
        
    # Logging Configuration
    LOGGING_LEVEL = 'INFO'
    LOG_FILE = 'app.log'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'