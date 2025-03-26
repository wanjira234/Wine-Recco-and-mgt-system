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
import re

auth_bp = Blueprint('auth', __name__)

# Form validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$')

# React Routes - These serve the React application
@auth_bp.route('/auth/login')
def react_login():
    """Serve the React-based login page."""
    return render_template('react_base.html')

@auth_bp.route('/auth/signup')
def react_signup():
    """Serve the React-based signup page."""
    return render_template('react_base.html')

@auth_bp.route('/auth/signup/step2')
def react_signup_step2():
    """Serve the React-based signup step 2 page."""
    return render_template('react_base.html')

@auth_bp.route('/auth/signup/step3')
def react_signup_step3():
    """Serve the React-based signup step 3 page."""
    return render_template('react_base.html')

# API endpoints for authentication
@auth_bp.route('/api/auth/signup', methods=['GET', 'POST', 'OPTIONS'])
def api_signup_handler():
    """Handle signup requests"""
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = current_app.make_default_options_response()
        return response

    # Handle GET request - return form requirements
    if request.method == 'GET':
        return jsonify({
            'requirements': {
                'step1': {
                    'email': 'Valid email address',
                    'password': 'At least 8 characters with letters and numbers',
                    'name': 'Your full name'
                },
                'step2': {
                    'wine_types': 'Select your preferred wine types',
                    'price_range': 'Choose your preferred price range',
                    'regions': 'Select your favorite wine regions'
                },
                'step3': {
                    'flavors': 'Select your preferred flavors',
                    'characteristics': 'Choose wine characteristics'
                }
            },
            'total_steps': 3,
            'current_step': 1
        })

    # Handle POST request
    try:
        data = request.get_json()
        step = data.get('step', 1)
        
        if step == 1:
            # Validate input for step 1
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            required_fields = ['email', 'password', 'name']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'message': f'Missing {field}'}), 400
            
            # Validate email format
            if not EMAIL_REGEX.match(data.get('email')):
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            # Validate password strength
            if not PASSWORD_REGEX.match(data.get('password')):
                return jsonify({
                    'success': False, 
                    'message': 'Password must be at least 8 characters and contain both letters and numbers'
                }), 400
            
            # Check if user already exists
            if User.query.filter_by(email=data.get('email')).first():
                return jsonify({'success': False, 'message': 'Email already registered'}), 409
            
            # Create new user
            new_user = User(
                email=data.get('email'),
                username=data.get('name'),
                password_hash=generate_password_hash(data.get('password')),
                signup_step=1
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            
            # Create access token
            access_token = create_access_token(identity=new_user.id)
            
            return jsonify({
                'success': True, 
                'message': 'Account created successfully! Let\'s set up your wine preferences.',
                'next_step': 2,
                'user': {
                    'id': new_user.id,
                    'email': new_user.email,
                    'name': new_user.username
                },
                'access_token': access_token
            })
            
        elif step == 2:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            # Update wine preferences
            user.wine_preferences = {
                'wine_types': data.get('wine_types', []),
                'price_range': data.get('price_range'),
                'regions': data.get('regions', [])
            }
            user.signup_step = 2
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Wine preferences saved! Let\'s set up your taste profile.',
                'next_step': 3
            })
            
        elif step == 3:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            # Update taste preferences
            user.taste_preferences = {
                'flavors': data.get('flavors', []),
                'sweetness': data.get('sweetness'),
                'acidity': data.get('acidity'),
                'tannin': data.get('tannin'),
                'body': data.get('body')
            }
            user.signup_step = 3  # Completed all steps
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile complete! Welcome to Wine Recommender.',
                'completed': True
            })
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during signup step {step}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error during signup step {step}'}), 500

@auth_bp.route('/api/auth/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    """Delete the current user's account"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Log out the user
        logout_user()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting account'}), 500