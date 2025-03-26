from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Wine, WineCategory, WineTrait

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main React application"""
    return render_template('react_base.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('react_base.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('react_base.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

@main_bp.route('/wines')
def get_wines():
    """Get all wines"""
    wines = Wine.query.all()
    return jsonify([wine.to_dict() for wine in wines])

@main_bp.route('/wines/<int:wine_id>')
def get_wine(wine_id):
    """Get a specific wine"""
    wine = Wine.query.get_or_404(wine_id)
    return jsonify(wine.to_dict())

@main_bp.route('/categories')
def get_categories():
    """Get all wine categories"""
    categories = WineCategory.query.all()
    return jsonify([category.to_dict() for category in categories])

@main_bp.route('/traits')
def get_traits():
    """Get all wine traits"""
    traits = WineTrait.query.all()
    return jsonify([trait.to_dict() for trait in traits])

@main_bp.route('/user/current')
@login_required
def get_current_user():
    """Get current user data"""
    return jsonify(current_user.to_dict()) 