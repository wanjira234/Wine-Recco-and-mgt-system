from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Wine, WineCategory, WineTrait

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main React application"""
    return render_template('react_base.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Serve the React dashboard"""
    return render_template('react_base.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Serve the React profile page"""
    return render_template('react_base.html')

@main_bp.route('/wines')
def wines():
    """Serve the React wines page"""
    return render_template('react_base.html')

@main_bp.route('/wines/<int:wine_id>')
def wine_detail(wine_id):
    """Serve the React wine detail page"""
    return render_template('react_base.html')

@main_bp.route('/search')
def search():
    """Serve the React search page"""
    return render_template('react_base.html')

@main_bp.route('/about')
def about():
    """Serve the React about page"""
    return render_template('react_base.html')

@main_bp.route('/contact')
def contact():
    """Serve the React contact page"""
    return render_template('react_base.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
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