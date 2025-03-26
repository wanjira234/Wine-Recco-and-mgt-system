from flask import Blueprint, render_template, jsonify
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Serve the React application"""
    return render_template('react_base.html')

@main.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@main.route('/api/user/current')
def get_current_user():
    """Get current user data"""
    if current_user.is_authenticated:
        return jsonify(current_user.to_dict())
    return jsonify({"error": "Not authenticated"}), 401 