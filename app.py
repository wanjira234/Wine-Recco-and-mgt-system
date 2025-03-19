import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity

# Import extensions
from extensions import db, socketio, mail, celery, cache

# Import Blueprints
from blueprints.auth import auth_bp
from blueprints.wines import wines_bp
from blueprints.cart import cart_bp
from blueprints.admin import admin_bp
from blueprints.recommendation import recommendation_bp
from blueprints.interaction import interaction_bp
from blueprints.wine_discovery import wine_discovery_bp
from blueprints.analytics import analytics_bp
from blueprints.order import order_bp
from blueprints.inventory import inventory_bp
from blueprints.community import community_bp
from blueprints.notification import notification_bp
from blueprints.search import search_bp

# Import Utilities and Services
from utils.error_handlers import register_error_handlers
from utils.cache_utils import clear_all_caches
from services.recommendation_service import create_recommendation_engine, RecommendationEngine
from services.wine_discovery_service import create_wine_discovery_service

# Import Models
from models import User

def configure_logging(app):
    """
    Configure comprehensive logging for the application
    """
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    
    # File Handler with Rotation
    file_handler = RotatingFileHandler(
        'app.log', 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Configure app logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Set log levels for external libraries
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('flask').setLevel(logging.WARNING)

def create_app():
    """
    Application Factory Function
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Configure Logging
    configure_logging(app)
    logger = app.logger

    try:
        # Initialize Extensions
        db.init_app(app)
        migrate = Migrate(app, db)
        
        # JWT Manager
        jwt = JWTManager(app)
        
        # CORS Configuration
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "allow_headers": [
                    "Content-Type", 
                    "Authorization", 
                    "Access-Control-Allow-Credentials"
                ]
            }
        })
        
        # Cache Initialization with Fallback
        try:
            cache.init_app(app, config={
                'CACHE_TYPE': app.config.get('CACHE_TYPE', 'redis'),
                'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
                'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            })
            logger.info("Cache initialized successfully")
        except Exception as cache_error:
            logger.warning(f"Redis cache failed, using simple cache: {cache_error}")
            cache.init_app(app, config={'CACHE_TYPE': 'simple'})
        
        # Login Manager Setup
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))
        
        # Initialize Other Extensions
        socketio.init_app(app)
        mail.init_app(app)
        
        # Celery Configuration
        celery.conf.update(app.config)
        
        # Register Blueprints
        blueprints = [
            (auth_bp, '/api/auth'),
            (cart_bp, '/api/cart'),
            (admin_bp, '/api/admin'),
            (recommendation_bp, '/api/recommendations'),
            (interaction_bp, '/api/interactions'),
            (wine_discovery_bp, '/api/wine-discovery'),
            (analytics_bp, '/api/analytics'),
            (order_bp, '/api/orders'),
            (inventory_bp, '/api/inventory'),
            (community_bp, '/api/community'),
            (notification_bp, '/api/notifications'),
            (search_bp, '/api/search'),
            (wines_bp, '/api/wines')
        ]
        
        for blueprint, url_prefix in blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        
        # Initialize Services within Application Context
        with app.app_context():
            # Create database tables
            db.create_all()
            
            # Initialize Recommendation Engine
            try:
                recommendation_engine = create_recommendation_engine()
                logger.info("Recommendation engine initialized successfully")
            except Exception as recommendation_error:
                logger.error(f"Failed to initialize recommendation engine: {recommendation_error}")
            
            # Initialize Wine Discovery Service
            try:
                wine_discovery_service = create_wine_discovery_service()
                logger.info("Wine discovery service initialized successfully")
            except Exception as discovery_error:
                logger.error(f"Failed to initialize wine discovery service: {discovery_error}")
        
        # WebSocket Authentication and Event Handlers
        @socketio.on('connect')
        def handle_connect():
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                join_room(f'user_{user_id}')
                logger.info(f"User {user_id} connected")
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
        
        @socketio.on('disconnect')
        def handle_disconnect():
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                leave_room(f'user_{user_id}')
                logger.info(f"User {user_id} disconnected")
            except Exception as e:
                logger.error(f"WebSocket disconnection error: {e}")
        
        # Global Error Handlers
        register_error_handlers(app)
        
        # CLI Commands
        @app.cli.command("init-db")
        def init_db():
            """Initialize the database"""
            with app.app_context():
                db.create_all()
                print("Database initialized.")
        
        @app.cli.command("clear-caches")
        def clear_caches():
            """Clear all application caches"""
            with app.app_context():
                clear_all_caches()
                print("All caches cleared.")
        
        return app
    
    except Exception as app_init_error:
        logger.error(f"Application initialization failed: {app_init_error}")
        raise

# Create App Instance
app = create_app()

if __name__ == '__main__':
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True
    )