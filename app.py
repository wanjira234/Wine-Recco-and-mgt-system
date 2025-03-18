from flask import Flask, render_template, jsonify
from services.wine_discovery_service import create_wine_discovery_service, wine_discovery_service
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Wine
from blueprints.auth import auth_bp
from blueprints.wines import wines_bp
from blueprints.cart import cart_bp
from blueprints.admin import admin_bp
from blueprints.recommendation import recommendation_bp
from services.recommendation_service import RecommendationEngine
from services.inventory_service import inventory_service
from flask_login import login_required, current_user
import logging
from flask_jwt_extended import get_jwt_identity
from extensions import db, socketio, mail, celery, cache
from commands import index_wines_command
from blueprints.interaction import interaction_bp
from blueprints.wine_discovery import wine_discovery_bp
from blueprints.analytics import analytics_bp
from blueprints.order import order_bp
from blueprints.inventory import inventory_bp
from blueprints.community import community_bp
from blueprints.notification import notification_bp
from blueprints.search import search_bp
from utils.error_handlers import register_error_handlers

# Import cache utilities
from utils.cache_utils import clear_all_caches

# Initialize recommendation engine globally
recommendation_engine = RecommendationEngine()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Enhanced Logging Configuration
    def configure_logging(app):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log', mode='a', encoding='utf-8')
            ]
        )
        
        # Set log levels for external libraries
        logging.getLogger('elasticsearch').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Call logging configuration
    configure_logging(app)
    logger = logging.getLogger(__name__)

    # Initialize extensions with error handling
    try:
        db.init_app(app)
        migrate = Migrate(app, db)
        socketio.init_app(app)
        mail.init_app(app)

        # Advanced Cache Initialization with Fallback
        try:
            cache.init_app(app, config={
                'CACHE_TYPE': app.config.get('CACHE_TYPE', 'redis'),
                'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
                'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            })
            logger.info("Cache initialized successfully")
        except Exception as cache_error:
            logger.warning(f"Primary cache initialization failed. Falling back to simple cache. Error: {cache_error}")
            cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    except Exception as ext_error:
        logger.error(f"Extension initialization failed: {ext_error}")
        raise

    # Login Manager Configuration
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

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

    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wines_bp, url_prefix='/api/wines')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    app.cli.add_command(index_wines_command)
    app.register_blueprint(interaction_bp, url_prefix='/interactions')
    app.register_blueprint(wine_discovery_bp, url_prefix='/wine-discovery')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    from blueprints.order import order_bp
    app.register_blueprint(order_bp, url_prefix='/api/orders')    
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(search_bp, url_prefix='/search')
    

    # Celery Configuration
    celery.conf.update(app.config)

    # Initialize Recommendation Engine
    with app.app_context():
        try:
            recommendation_engine.load_wine_data()
            logger.info("Recommendation engine initialized successfully")
            
            # Initialize wine discovery service
            wine_discovery_service = create_wine_discovery_service(app)
        except Exception as init_error:
            logger.error(f"Initialization error: {init_error}")

    # Advanced Error Handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Global error handler for unhandled exceptions
        """
        logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500

    # WebSocket Event Handlers
    @socketio.on('connect')
    def handle_connect():
        try:
            user_id = get_jwt_identity()
            join_room(f'user_{user_id}')
            logger.info(f"User {user_id} connected")
        except Exception as e:
            logger.error(f"Connection error: {e}")

    @socketio.on('disconnect')
    def handle_disconnect():
        try:
            user_id = get_jwt_identity()
            leave_room(f'user_{user_id}')
            logger.info(f"User {user_id} disconnected")
        except Exception as e:
            logger.error(f"Disconnection error: {e}")

    # Optional: Add CLI command to clear caches
    @app.cli.command("clear-caches")
    def clear_caches_command():
        """Clear all application caches"""
        clear_all_caches()
        logger.info("All caches cleared successfully")

     # Register global error handlers
    register_error_handlers(app)

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)