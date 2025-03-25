import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Import extensions
from extensions import db, socketio, mail, celery, cache, csrf

# Import Blueprints
from blueprints.main import main_bp
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
from blueprints.account import account_bp

# Import Utilities and Services
from utils.error_handlers import register_error_handlers
from utils.cache_utils import clear_all_caches
from services.recommendation_service import create_recommendation_engine, RecommendationEngine
from services.wine_discovery_service import create_wine_discovery_service

# Import Models
from models import User, WineTrait

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
    app = Flask(__name__, 
        static_folder='static',
        static_url_path='/static'
    )
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Set secret key for CSRF protection
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
    
    # Initialize CSRF protection
    csrf.init_app(app)
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY', 'your-csrf-secret-key')
    app.config['WTF_CSRF_ENABLED'] = True
    
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
        
        # API Documentation route
        @app.route('/api')
        def api_docs():
            return jsonify({
                "message": "Welcome to the Wine Recommender API",
                "version": "1.0.0",
                "endpoints": {
                    "auth": "/api/auth/",
                    "wines": "/api/wines/",
                    "recommendations": "/api/recommendations/",
                    "cart": "/api/cart/",
                    "orders": "/api/orders/",
                    "community": "/api/community/",
                    "search": "/api/search/"
                },
                "documentation": "Please refer to the API documentation for detailed information about each endpoint."
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
        login_manager.login_message_category = 'info'

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
            (main_bp, ''),  # Main blueprint for frontend pages
            (auth_bp, '/auth'),  # Changed from '/api/auth' to '/auth'
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
            (wines_bp, '/api/wines'),
            (account_bp, '/account')
        ]
        
        for blueprint, url_prefix in blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        
        # Initialize Services within Application Context
        with app.app_context():
            # Create database tables
            try:
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as db_error:
                logger.error(f"Failed to create database tables: {db_error}")
                raise
            
            # Initialize Recommendation Engine
            try:
                from services.recommendation_service import get_recommendation_engine
                # Only initialize if not already initialized
                if not hasattr(app, 'recommendation_engine'):
                    app.recommendation_engine = get_recommendation_engine()
                    logger.info("Recommendation engine initialized successfully")
            except Exception as recommendation_error:
                logger.error(f"Failed to initialize recommendation engine: {recommendation_error}")
                app.recommendation_engine = None
            
            # Initialize Wine Discovery Service
            try:
                if not hasattr(app, 'wine_discovery_service'):
                    app.wine_discovery_service = create_wine_discovery_service()
                    logger.info("Wine discovery service initialized successfully")
            except Exception as discovery_error:
                logger.error(f"Failed to initialize wine discovery service: {discovery_error}")
                app.wine_discovery_service = None
        
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
        
        @app.cli.command("create-admin")
        def create_admin():
            """Create an admin user"""
            try:
                username = input("Enter admin username: ")
                email = input("Enter admin email: ")
                password = input("Enter admin password: ")
                
                user = User(
                    username=username,
                    email=email,
                    is_admin=True
                )
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                print(f"Admin user '{username}' created successfully!")
            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.session.rollback()
        
        @app.cli.command("populate-traits")
        def populate_traits():
            """Populate wine traits in the database"""
            try:
                # Define trait categories
                trait_categories = {
                    'taste': ['sweet', 'dry', 'tart', 'crisp', 'tangy', 'juicy', 'rich', 'smooth', 'soft', 'sharp'],
                    'aroma': ['almond', 'anise', 'apple', 'apricot', 'berry', 'black_cherry', 'blackberry', 'blueberry', 
                             'citrus', 'peach', 'pear', 'plum', 'raspberry', 'strawberry', 'tropical_fruit', 'vanilla',
                             'chocolate', 'coffee', 'caramel', 'honey', 'spice', 'cinnamon', 'nutmeg', 'pepper'],
                    'body': ['light_bodied', 'medium_bodied', 'full_bodied', 'dense', 'thick', 'weight', 'robust', 'hearty'],
                    'texture': ['silky', 'velvety', 'smooth', 'round', 'plush', 'supple', 'firm', 'tannin', 'gripping'],
                    'character': ['complex', 'elegant', 'fresh', 'vibrant', 'bright', 'powerful', 'concentrated', 'refined'],
                    'notes': ['floral', 'herbal', 'earthy', 'mineral', 'oak', 'smoke', 'leather', 'tobacco', 'cedar']
                }

                # Create traits for each category
                for category, traits in trait_categories.items():
                    for trait_name in traits:
                        # Check if trait already exists
                        existing_trait = WineTrait.query.filter_by(name=trait_name).first()
                        if not existing_trait:
                            trait = WineTrait(
                                name=trait_name,
                                category=category,
                                description=f"{trait_name.replace('_', ' ').title()} characteristic in wines"
                            )
                            db.session.add(trait)
                
                # Add remaining traits as 'other'
                all_traits = ['almond', 'anise', 'apple', 'apricot', 'baked', 'baking_spices', 'berry', 'black_cherry', 
                            'black_currant', 'black_pepper', 'black_tea', 'blackberry', 'blueberry', 'boysenberry', 
                            'bramble', 'bright', 'butter', 'candy', 'caramel', 'cardamom', 'cassis', 'cedar', 'chalk', 
                            'cherry', 'chocolate', 'cinnamon', 'citrus', 'clean', 'closed', 'clove', 'cocoa', 'coffee', 
                            'cola', 'complex', 'concentrated', 'cranberry', 'cream', 'crisp', 'dark', 'dark_chocolate', 
                            'dense', 'depth', 'dried_herb', 'dry', 'dust', 'earth', 'edgy', 'elderberry', 'elegant', 
                            'fennel', 'firm', 'flower', 'forest_floor', 'french_oak', 'fresh', 'fruit', 'full_bodied', 
                            'game', 'grapefruit', 'graphite', 'green', 'gripping', 'grippy', 'hearty', 'herb', 'honey', 
                            'honeysuckle', 'jam', 'juicy', 'lavender', 'leafy', 'lean', 'leather', 'lemon', 'lemon_peel', 
                            'length', 'licorice', 'light_bodied', 'lime', 'lush', 'meaty', 'medium_bodied', 'melon', 
                            'milk_chocolate', 'minerality', 'mint', 'nutmeg', 'oak', 'olive', 'orange', 'orange_peel', 
                            'peach', 'pear', 'pencil_lead', 'pepper', 'pine', 'pineapple', 'plum', 'plush', 'polished', 
                            'pomegranate', 'powerful', 'purple', 'purple_flower', 'raspberry', 'refreshing', 'restrained', 
                            'rich', 'ripe', 'robust', 'rose', 'round', 'sage', 'salt', 'savory', 'sharp', 'silky', 
                            'smoke', 'smoked_meat', 'smooth', 'soft', 'sparkling', 'spice', 'steel', 'stone', 'strawberry', 
                            'succulent', 'supple', 'sweet', 'tangy', 'tannin', 'tar', 'tart', 'tea', 'thick', 'thyme', 
                            'tight', 'toast', 'tobacco', 'tropical_fruit', 'vanilla', 'velvety', 'vibrant', 'violet', 
                            'warm', 'weight', 'wet_rocks', 'white', 'white_pepper', 'wood']

                existing_traits = {t.name for t in WineTrait.query.all()}
                for trait_name in all_traits:
                    if trait_name not in existing_traits:
                        trait = WineTrait(
                            name=trait_name,
                            category='other',
                            description=f"{trait_name.replace('_', ' ').title()} characteristic in wines"
                        )
                        db.session.add(trait)

                db.session.commit()
                print("Wine traits populated successfully!")
                
            except Exception as e:
                print(f"Error populating wine traits: {e}")
                db.session.rollback()
        
        # Add template context processor
        @app.context_processor
        def inject_now():
            from datetime import datetime
            return {'now': datetime.utcnow()}
        
        return app
    
    except Exception as app_init_error:
        logger.error(f"Application initialization failed: {app_init_error}")
        raise

# Create App Instance
app = create_app()

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    print("\nStarting Flask development server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("API endpoints are available at: http://127.0.0.1:5000/api/")
    print("\nAvailable API endpoints:")
    print("- /api/auth/ - Authentication endpoints")
    print("- /api/wines/ - Wine management")
    print("- /api/recommendations/ - Wine recommendations")
    print("- /api/cart/ - Shopping cart")
    print("- /api/orders/ - Order management")
    print("- /api/community/ - Community features")
    print("- /api/search/ - Search functionality")
    print("\nPress CTRL+C to quit\n")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True
    )