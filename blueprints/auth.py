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

# Add login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('signup/login.html')

# Add logout route
@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/signup', methods=['GET'])
def signup():
    """Handle step 1 of signup process"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('signup/step1.html')

@auth_bp.route('/signup/step2', methods=['GET'])
@jwt_required()
def signup_step2():
    """Handle step 2 of signup process"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
            
        if user.signup_step != 1:
            flash('Please complete step 1 first', 'error')
            return redirect(url_for('auth.signup'))
            
        return render_template('signup/step2.html')
        
    except Exception as e:
        current_app.logger.error(f"Error in signup step 2: {str(e)}")
        flash('An error occurred', 'error')
        return redirect(url_for('auth.signup'))

@auth_bp.route('/signup/step3', methods=['GET', 'POST'])
@jwt_required()
def signup_step3():
    """Handle step 3 of the signup process"""
    if request.method == 'GET':
        return render_template('signup/step3.html')
        
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
            
        if user.signup_step != 2:
            flash('Please complete step 2 first', 'error')
            return redirect(url_for('auth.signup_step2'))
            
        # Get form data
        characteristics = request.form.getlist('characteristics')
        flavors = request.form.getlist('flavors')
        
        if not characteristics or not flavors:
            flash('Please select at least one characteristic and one flavor', 'error')
            return redirect(url_for('auth.signup_step3'))
            
        # Update user preferences
        user.taste_preferences = {
            'characteristics': characteristics,
            'flavors': flavors
        }
        user.signup_step = 3  # Mark step 3 as completed
        db.session.commit()
        
        flash('Your wine preferences have been saved!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in signup step 3: {str(e)}")
        flash('An error occurred while saving your preferences', 'error')
        return redirect(url_for('auth.signup_step3'))