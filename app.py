from flask import Flask, render_template, jsonify
from services.wine_discovery_service import create_wine_discovery_service
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
from flask_login import login_required, current_user
import logging
from flask_jwt_extended import get_jwt_identity
from extensions import socketio, mail
from commands import index_wines_command
from blueprints.interaction import interaction_bp
from blueprints.wine_discovery import wine_discovery_bp
from blueprints.analytics import analytics_bp
from blueprints.order import order_bp
from blueprints.inventory import inventory_bp
from blueprints.community import community_bp
from blueprints.notification import notification_bp
from blueprints.search import search_bp

# Initialize recommendation engine globally
recommendation_engine = RecommendationEngine()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app)
    mail.init_app(app)

    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # User loader
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
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    app.register_blueprint(search_bp, url_prefix='/search')
    
    # Initialize recommendation data when app starts
    global _wine_discovery_service
    
    with app.app_context():
        try:
            recommendation_engine.load_wine_data()
            logger.info("Recommendation engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation engine: {str(e)}")
        wine_discovery_service = create_wine_discovery_service(app)

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal Server Error"}), 500

    # Catch-all route for React frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('react_app.html')
    
    socketio.init_app(app)
    
    # WebSocket Event Handlers
    @socketio.on('connect')
    def handle_connect():
        user_id = get_jwt_identity()
        join_room(f'user_{user_id}')

    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = get_jwt_identity()
        leave_room(f'user_{user_id}')

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)