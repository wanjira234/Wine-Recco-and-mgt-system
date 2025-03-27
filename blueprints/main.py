from flask import Blueprint, render_template, jsonify, request, url_for, current_app
from flask_login import login_required, current_user
from models import Wine, WineCategory, WineTrait
from flask_wtf.csrf import generate_csrf

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main home page"""
    config_data = {
        'apiUrl': url_for('api_docs', _external=True),
        'environment': current_app.config.get('ENV', 'development'),
        'debug': current_app.config.get('DEBUG', False),
        'csrfToken': generate_csrf()
    }
    return render_template('home.html', config_data=config_data)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Serve the dashboard page"""
    return render_template('home.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Serve the profile page"""
    return render_template('home.html')

@main_bp.route('/catalog')
def catalog():
    """Serve the catalog page"""
    return render_template('catalog.html')

@main_bp.route('/about')
def about():
    """Serve the about page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Serve the contact page"""
    return render_template('contact.html')

@main_bp.route('/predict')
def predict():
    """Serve the prediction page"""
    return render_template('predict.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': current_app.config.get('VERSION', '1.0.0')
    })

@main_bp.route('/api/wines')
def get_wines():
    """Get all wines"""
    wines = Wine.query.all()
    return jsonify([wine.to_dict() for wine in wines])

@main_bp.route('/api/wines/<int:wine_id>')
def get_wine(wine_id):
    """Get a specific wine"""
    wine = Wine.query.get_or_404(wine_id)
    return jsonify(wine.to_dict())

@main_bp.route('/api/categories')
def get_categories():
    """Get all wine categories"""
    categories = WineCategory.query.all()
    return jsonify([category.to_dict() for category in categories])

@main_bp.route('/api/traits')
def get_traits():
    """Get all wine traits"""
    traits = WineTrait.query.all()
    return jsonify([trait.to_dict() for trait in traits])

@main_bp.route('/api/user/current')
@login_required
def get_current_user():
    """Get current user data"""
    return jsonify(current_user.to_dict()) 