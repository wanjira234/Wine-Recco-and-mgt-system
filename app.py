from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Wine
from blueprints.auth import auth_bp
from blueprints.wines import wines_bp
from blueprints.cart import cart_bp
from blueprints.admin import admin_bp
from services.recommendation_service import recommendation_engine
from flask_login import login_required, current_user
import logging
from commands import index_wines_command
from blueprints.interaction import interaction_bp
from blueprints.wine_discovery import wine_discovery_bp
from blueprints.analytics import analytics_bp
from blueprints.order import order_bp
from blueprints.inventory import inventory_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
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
    app.cli.add_command(index_wines_command)
    app.register_blueprint(interaction_bp, url_prefix='/interactions')
    app.register_blueprint(wine_discovery_bp, url_prefix='/wine-discovery')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    
    # ... rest of the code
    # Initialize recommendation data when app starts
    with app.app_context():
        try:
            recommendation_engine.prepare_recommendation_data()
            logger.info("Recommendation engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation engine: {str(e)}")

    # Recommendation Routes
    @wines_bp.route('/recommendations', methods=['GET'])
    @login_required
    def get_wine_recommendations():
        try:
            # Get recommendations for the current user
            recommended_wine_ids = recommendation_engine.hybrid_recommendation(
                current_user.id
            )

            # Fetch wine details
            recommended_wines = Wine.query.filter(Wine.id.in_(recommended_wine_ids)).all()

            return jsonify({
                'recommendations': [
                    {
                        'id': wine.id,
                        'name': wine.name,
                        'type': wine.type,
                        'region': wine.region,
                        'price': wine.price,
                        'image_url': wine.image_url,
                        'description': wine.description
                    } for wine in recommended_wines
                ]
            })
        except Exception as e:
            # Log the error and return a generic error response
            logger.error(f"Recommendation error: {str(e)}")
            return jsonify({
                'error': 'Failed to generate recommendations',
                'details': str(e)
            }), 500

    # Optional: Add a route to manually refresh recommendations
    @wines_bp.route('/refresh-recommendations', methods=['POST'])
    @login_required
    def refresh_recommendations():
        try:
            recommendation_engine.prepare_recommendation_data()
            return jsonify({
                'message': 'Recommendation engine refreshed successfully'
            }), 200
        except Exception as e:
            logger.error(f"Recommendation refresh error: {str(e)}")
            return jsonify({
                'error': 'Failed to refresh recommendation engine',
                'details': str(e)
            }), 500

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

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)