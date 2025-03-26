from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Wine, WineCategory, WineTrait

main = Blueprint('main', __name__)

@main.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@main.route('/wines')
def get_wines():
    """Get all wines"""
    wines = Wine.query.all()
    return jsonify([wine.to_dict() for wine in wines])

@main.route('/wines/<int:wine_id>')
def get_wine(wine_id):
    """Get a specific wine"""
    wine = Wine.query.get_or_404(wine_id)
    return jsonify(wine.to_dict())

@main.route('/categories')
def get_categories():
    """Get all wine categories"""
    categories = WineCategory.query.all()
    return jsonify([category.to_dict() for category in categories])

@main.route('/traits')
def get_traits():
    """Get all wine traits"""
    traits = WineTrait.query.all()
    return jsonify([trait.to_dict() for trait in traits])

@main.route('/user/current')
@login_required
def get_current_user():
    """Get current user data"""
    return jsonify(current_user.to_dict()) 