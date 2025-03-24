from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_mail import Mail
from celery import Celery
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()
celery = Celery(__name__, broker='redis://localhost:6379/0')

# Initialize Cache with a fallback
cache = Cache()
csrf = CSRFProtect()