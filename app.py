import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from models import User, WineTrait, WineCategory, Wine, WineReview, Order, OrderItem, WineInventory
from decimal import Decimal
import json
from jinja2 import Undefined
from functools import wraps
import uuid
import inspect
import traceback

# // ...existing code...
from blueprints.notification import notification_bp
from blueprints.search import search_bp
from blueprints.account import account_bp
# // ...existing code...

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

# Import Utilities and Services
from utils.error_handlers import register_error_handlers
from utils.cache_utils import clear_all_caches
from services.recommendation_service import create_recommendation_engine, RecommendationEngine
from services.wine_discovery_service import create_wine_discovery_service

# Function to sanitize data before JSON serialization
def sanitize_for_json(obj):
    """Recursively sanitize data for JSON serialization"""
    if obj is None or isinstance(obj, Undefined):
        return None
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if not isinstance(v, Undefined)}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj if not isinstance(item, Undefined)]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return sanitize_for_json(obj.to_dict())
    if isinstance(obj, (str, int, float, bool)):
        return obj
    try:
        return str(obj)
    except:
        return None

# Decorator to apply JSON sanitization to return values
def json_safe(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, tuple):
            # Handle tuple return (data, status_code)
            data, *rest = result
            return (sanitize_for_json(data), *rest)
        else:
            # Handle single return value
            return sanitize_for_json(result)
    return decorated_function

# Monkey patch Flask's jsonify to use sanitization
original_jsonify = jsonify
def safe_jsonify(*args, **kwargs):
    # Sanitize args and kwargs before passing to jsonify
    sanitized_args = [sanitize_for_json(arg) for arg in args]
    sanitized_kwargs = {k: sanitize_for_json(v) for k, v in kwargs.items()}
    return original_jsonify(*sanitized_args, **sanitized_kwargs)

# Replace Flask's jsonify with our safe version
jsonify = safe_jsonify

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable types"""
    def default(self, obj):
        try:
            if isinstance(obj, Undefined):
                return None
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, uuid.UUID):
                return str(obj)
            if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
                return obj.to_dict()
            return super().default(obj)
        except Exception as e:
            current_app.logger.error(f"JSON encoding error: {e}")
            return None

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
    
    # Set environment configuration
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    
    # Set secret key for CSRF protection
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
    
    # Initialize CSRF protection
    csrf.init_app(app)
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY', 'your-csrf-secret-key')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable default CSRF checking
    
    # Configure Logging
    configure_logging(app)
    logger = app.logger

    try:
        # Initialize Extensions
        db.init_app(app)
        migrate = Migrate(app, db)
        
        # Check database migrations status
        with app.app_context():
            from flask_migrate import current
            from alembic.script import ScriptDirectory
            from alembic.runtime.migration import MigrationContext
            
            # Get current migration version
            conn = db.engine.connect()
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            
            # Get latest available migration
            config = migrate.get_config()
            script = ScriptDirectory.from_config(config)
            head_rev = script.get_current_head()
            
            if current_rev != head_rev:
                logger.warning("Database schema is not up to date!")
                logger.warning("Current revision: %s", current_rev)
                logger.warning("Latest revision: %s", head_rev)
                logger.warning("Please run: flask db upgrade")
        
        # JWT Manager
        jwt = JWTManager(app)
        
        # CORS Configuration
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type", 
                    "Authorization", 
                    "X-CSRFToken",
                    "Access-Control-Allow-Credentials"
                ]
            }
        })
        
        # Set JSON encoder
        app.json_encoder = CustomJSONEncoder
        
        # Add template context processor for config
        @app.context_processor
        def inject_config():
            return {
                'config': {
                    'ENV': app.config.get('ENV', 'development'),
                    'DEBUG': app.config.get('DEBUG', False)
                }
            }
        
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
        
        # Register error handlers
        register_error_handlers(app)

        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(wines_bp, url_prefix='/api/wines')
        app.register_blueprint(cart_bp, url_prefix='/api/cart')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
        app.register_blueprint(interaction_bp, url_prefix='/api/interactions')
        app.register_blueprint(wine_discovery_bp, url_prefix='/api/discover')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(order_bp, url_prefix='/api/orders')
        app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
        app.register_blueprint(community_bp, url_prefix='/api/community')
        app.register_blueprint(notification_bp, url_prefix='/api/notifications')
        app.register_blueprint(search_bp, url_prefix='/api/search')
        app.register_blueprint(account_bp, url_prefix='/api/account')

        # Initialize services with error handling
        with app.app_context():
            try:
                recommendation_engine = create_recommendation_engine()
                app.config['recommendation_engine'] = recommendation_engine
            except Exception as e:
                from utils.error_handlers import handle_initialization_error
                handle_initialization_error(e, "Recommendation Engine")
                app.config['recommendation_engine'] = None

            try:
                wine_discovery_service = create_wine_discovery_service()
                app.config['wine_discovery_service'] = wine_discovery_service
            except Exception as e:
                from utils.error_handlers import handle_initialization_error
                handle_initialization_error(e, "Wine Discovery Service")
                app.config['wine_discovery_service'] = None

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
        
        # CLI Commands
        @app.cli.command("init-db")
        def init_db():
            """Initialize the database with all tables and initial data"""
            try:
                # Create all tables
                db.create_all()
                
                # Check if we need to populate initial data
                if not WineCategory.query.first():
                    # Populate wine categories
                    categories = [
                        {'name': 'Red Wine', 'description': 'Wines made from red or black grapes'},
                        {'name': 'White Wine', 'description': 'Wines made from white grapes'},
                        {'name': 'Rosé Wine', 'description': 'Wines with a pink color, made from red grapes'},
                        {'name': 'Sparkling Wine', 'description': 'Wines with significant levels of carbon dioxide'},
                    ]
                    
                    for category_data in categories:
                        category = WineCategory(**category_data)
                        db.session.add(category)
                    
                    db.session.commit()
                    print("Wine categories populated successfully!")
                
                # Verify tables were created
                with db.engine.connect() as conn:
                    tables = db.inspect(db.engine).get_table_names()
                    print("\nCreated tables:")
                    for table in tables:
                        print(f"- {table}")
                
                print("\nDatabase initialized successfully!")
                
            except Exception as e:
                print(f"Error initializing database: {e}")
                db.session.rollback()
                raise
        
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
        
        @app.cli.command("populate-categories")
        def populate_categories():
            """Populate wine categories in the database"""
            try:
                categories = [
                    {
                        'name': 'Red Wine',
                        'description': 'Wines made from red or black grapes'
                    },
                    {
                        'name': 'White Wine',
                        'description': 'Wines made from white grapes'
                    },
                    {
                        'name': 'Rosé Wine',
                        'description': 'Wines with a pink color, made from red grapes'
                    },
                    {
                        'name': 'Sparkling Wine',
                        'description': 'Wines with significant levels of carbon dioxide'
                    },
                ]

                for category_data in categories:
                    category = WineCategory.query.filter_by(name=category_data['name']).first()
                    if not category:
                        category = WineCategory(**category_data)
                        db.session.add(category)

                db.session.commit()
                print("Wine categories populated successfully!")
                
            except Exception as e:
                print(f"Error populating wine categories: {e}")
                db.session.rollback()
        
        # Add template context processor
        @app.context_processor
        def inject_now():
            from datetime import datetime
            return {'now': datetime.utcnow()}
        
        # CSRF Protection for API routes
        @app.before_request
        def csrf_protect():
            if request.path.startswith('/api/'):
                if request.method != 'OPTIONS':  # Skip CSRF check for preflight requests
                    csrf_token = request.headers.get('X-CSRFToken')
                    if not csrf_token and request.method not in ['GET', 'HEAD', 'OPTIONS']:
                        return jsonify({'error': 'CSRF token missing'}), 400
        
        return app
    
    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Create App Instance
app = create_app()

# Update the serve function to handle React routes properly
@app.route('/_next/<path:path>')
def next_static(path):
    return send_from_directory('_next', path)

# All other routes will be handled by Next.js
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('index.html')

# Remove conflicting error handlers
# The centralized error handling from utils.error_handlers will be used instead

if __name__ == '__main__':
    app = create_app()
    app.config['DEBUG'] = True
    
    # Serve Next.js static files
    @app.route('/_next/<path:path>')
    def next_static(path):
        return send_from_directory('_next', path)
    
    # All other routes will be handled by Next.js
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('index.html')
    
    print(" * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)")
    print(" * Next.js frontend will be available at http://127.0.0.1:3000/")
    app.run(debug=True, host='127.0.0.1', port=5000)