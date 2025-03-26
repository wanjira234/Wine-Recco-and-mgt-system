from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService
from forms import LoginForm, RegistrationForm, SignupForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, WineTrait
from extensions import db
from sqlalchemy import func
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# React Routes - These serve the React application
@auth_bp.route('/login')
def react_login():
    """Serve the React-based login page."""
    return render_template('react_base.html')

@auth_bp.route('/signup')
def react_signup():
    """Serve the React-based signup page."""
    return render_template('react_base.html')

@auth_bp.route('/signup/step2')
def react_signup_step2():
    """Serve the React-based signup step 2 page."""
    return render_template('react_base.html')

@auth_bp.route('/signup/step3')
def react_signup_step3():
    """Serve the React-based signup step 3 page."""
    return render_template('react_base.html')

# Traditional Flask Routes - These serve Flask templates
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Traditional Flask-based signup"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        # Existing signup logic
        pass
    
    return render_template('auth/signup.html')

@auth_bp.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    """Traditional Flask-based signup step 2"""
    if 'signup_data' not in session:
        return redirect(url_for('auth.signup'))
    
    if request.method == 'POST':
        # Existing step 2 logic
        pass
        
    return render_template('auth/signup_step2.html')

# API Endpoints - These serve the React frontend
@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for React signup form submission."""
    data = request.get_json()
    
    # Validate input
    if not all(key in data for key in ['email', 'password', 'first_name', 'last_name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    try:
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=generate_username(data['first_name'], data['last_name'])
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/signup/step2', methods=['POST'])
@jwt_required()
def api_signup_step2():
    """API endpoint for step 2 of the signup process."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = User.query.get(user_id)
        user.wine_preferences = data.get('wine_preferences', {})
        db.session.commit()
        return jsonify({'message': 'Preferences updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/signup/step3', methods=['POST'])
@jwt_required()
def api_signup_step3():
    """API endpoint for step 3 of the signup process."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = User.query.get(user_id)
        user.taste_preferences = data.get('taste_preferences', {})
        db.session.commit()
        return jsonify({'message': 'Preferences updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for React login form submission."""
    data = request.get_json()
    
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout')
@jwt_required()
def api_logout():
    """API endpoint for user logout."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/api/reset-password-request', methods=['POST'])
def api_reset_password_request():
    """API endpoint for password reset request."""
    data = request.get_json()
    
    try:
        reset_token = AuthService.reset_password_request(
            email=data.get('email')
        )
        return jsonify({'reset_token': reset_token}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """API endpoint for password reset."""
    data = request.get_json()
    
    try:
        user = AuthService.reset_password(
            reset_token=data.get('reset_token'),
            new_password=data.get('new_password')
        )
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/profile', methods=['PUT'])
@jwt_required()
def api_update_profile():
    """API endpoint for updating user profile."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = AuthService.update_user_profile(user_id, **data)
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/change-password', methods=['POST'])
@jwt_required()
def api_change_password():
    """API endpoint for changing user password."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = AuthService.change_password(
            user_id=user_id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def generate_username(first_name, last_name):
    """Generate a unique username from first and last name."""
    base = f"{first_name.lower()}{last_name.lower()}"
    username = base
    counter = 1
    
    while User.query.filter_by(username=username).first():
        username = f"{base}{counter}"
        counter += 1
    
    return username

@auth_bp.route('/signup/step3', methods=['GET'])
def signup_step3():
    if 'signup_data' not in session:
        return redirect(url_for('auth.signup'))
    # Get traits for the form
    traits_by_category = {
        'Body': ['light', 'medium', 'full'],
        'Sweetness': ['dry', 'off_dry', 'sweet'],
        'Tannin': ['low', 'medium', 'high'],
        'Acidity': ['low', 'medium', 'high'],
        'Age': ['young', 'medium', 'aged']
    }
    return render_template('auth/signup_step3.html', traits_by_category=traits_by_category)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    """
    Request password reset
    """
    data = request.get_json()
    
    try:
        reset_token = AuthService.reset_password_request(
            email=data.get('email')
        )
        return jsonify({'reset_token': reset_token}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token
    """
    data = request.get_json()
    
    try:
        user = AuthService.reset_password(
            reset_token=data.get('reset_token'),
            new_password=data.get('new_password')
        )
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = AuthService.update_user_profile(user_id, **data)
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = AuthService.change_password(
            user_id=user_id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# API endpoints for React
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
        
    try:
        new_user = User(
            username=data['username'],
            email=data['email'],
            created_at=datetime.utcnow()
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"API registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me')
@jwt_required()
def get_current_user():
    """Get current user information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(user.to_dict())