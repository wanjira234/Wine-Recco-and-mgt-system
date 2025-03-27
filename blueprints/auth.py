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
import traceback

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
                    'traits': 'Select your preferred wine traits and characteristics'
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
            
            # Generate unique username
            username = User.generate_unique_username(data.get('name'))
            
            # Create temporary user with signup data
            temp_user = User(
                email=data.get('email'),
                username=username,
                signup_step=1,
                signup_data={
                    'email': data.get('email'),
                    'password': data.get('password'),
                    'name': data.get('name')
                }
            )
            db.session.add(temp_user)
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=temp_user.id)
            
            return jsonify({
                'success': True, 
                'message': 'Let\'s set up your wine preferences.',
                'next_step': 2,
                'user': {
                    'id': temp_user.id,
                    'email': temp_user.email,
                    'name': temp_user.username
                },
                'access_token': access_token
            })
            
        elif step == 2:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            if user.signup_step != 1:
                return jsonify({'success': False, 'message': 'Please complete step 1 first'}), 400
            
            # Update signup data with wine preferences
            signup_data = user.signup_data or {}
            signup_data.update({
                'wine_types': data.get('wine_types', []),
                'price_range': data.get('price_range'),
                'regions': data.get('regions', [])
            })
            user.signup_data = signup_data
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
            
            if user.signup_step != 2:
                return jsonify({'success': False, 'message': 'Please complete step 2 first'}), 400
            
            # Get selected traits
            trait_ids = data.get('traits', [])
            selected_traits = WineTrait.query.filter(WineTrait.id.in_(trait_ids)).all()
            
            # Create final user with all data
            final_user = User(
                email=user.signup_data['email'],
                username=user.username,  # Keep the same username
                password_hash=generate_password_hash(user.signup_data['password']),
                wine_preferences={
                    'wine_types': user.signup_data.get('wine_types', []),
                    'price_range': user.signup_data.get('price_range'),
                    'regions': user.signup_data.get('regions', [])
                },
                signup_step=3,
                is_signup_complete=True
            )
            
            # Add selected traits
            final_user.preferred_traits = selected_traits
            
            # Delete temporary user and create final user
            db.session.delete(user)
            db.session.add(final_user)
            db.session.commit()
            
            # Log in the final user
            login_user(final_user)
            
            # Create new access token
            access_token = create_access_token(identity=final_user.id)
            
            return jsonify({
                'success': True,
                'message': 'Profile complete! Welcome to Wine Recommender.',
                'completed': True,
                'access_token': access_token
            })
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during signup step {step}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error during signup step {step}'}), 500

@auth_bp.route('/api/auth/delete-profile', methods=['POST'])
@jwt_required()
def delete_profile():
    """Delete the current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Delete the account
        if user.delete_account():
            # Log out the user
            logout_user()
            
            return jsonify({
                'success': True,
                'message': 'Profile deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete profile'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error deleting profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting profile'}), 500

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

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle signup API requests"""
    try:
        # Log the incoming request data
        current_app.logger.info("Received signup request")
        data = request.get_json()
        current_app.logger.info(f"Request data: {data}")
        
        step = data.get('step', 1)
        current_app.logger.info(f"Processing signup step: {step}")
        
        if step == 1:
            # Validate input for step 1
            if not data:
                current_app.logger.error("No data provided")
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            required_fields = ['email', 'password', 'name']
            for field in required_fields:
                if not data.get(field):
                    current_app.logger.error(f"Missing required field: {field}")
                    return jsonify({'success': False, 'message': f'Missing {field}'}), 400
            
            # Validate email format
            if not EMAIL_REGEX.match(data.get('email')):
                current_app.logger.error(f"Invalid email format: {data.get('email')}")
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            # Validate password strength
            if not PASSWORD_REGEX.match(data.get('password')):
                current_app.logger.error("Invalid password format")
                return jsonify({
                    'success': False, 
                    'message': 'Password must be at least 8 characters and contain both letters and numbers'
                }), 400
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=data.get('email')).first()
            if existing_user:
                current_app.logger.error(f"Email already registered: {data.get('email')}")
                return jsonify({'success': False, 'message': 'Email already registered'}), 409
            
            try:
                # Create temporary user with signup data
                temp_user = User(
                    email=data.get('email'),
                    username=User.generate_unique_username(data.get('name')),
                    signup_step=1,
                    signup_data={
                        'email': data.get('email'),
                        'password': data.get('password'),
                        'name': data.get('name')
                    }
                )
                db.session.add(temp_user)
                db.session.commit()
                
                # Create access token
                access_token = create_access_token(identity=temp_user.id)
                
                current_app.logger.info(f"Successfully created temporary user: {temp_user.id}")
                
                return jsonify({
                    'success': True, 
                    'message': 'Account created successfully! Let\'s set up your wine preferences.',
                    'next_step': 2,
                    'user': {
                        'id': temp_user.id,
                        'email': temp_user.email,
                        'name': temp_user.username
                    },
                    'access_token': access_token
                })
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Error creating user account'}), 500
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during signup: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e)}")
        current_app.logger.error(f"Exception traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Error during signup', 'error': str(e)}), 500

@auth_bp.route('/signup/step2', methods=['GET'])
def signup_step2():
    """Handle step 2 of signup process"""
    try:
        return render_template('signup/step2.html')
    except Exception as e:
        current_app.logger.error(f"Error in signup step 2: {str(e)}")
        flash('An error occurred', 'error')
        return redirect(url_for('auth.signup'))

@auth_bp.route('/signup/step3', methods=['GET'])
def signup_step3():
    """Handle step 3 of signup process"""
    try:
        return render_template('signup/step3.html')
    except Exception as e:
        current_app.logger.error(f"Error in signup step 3: {str(e)}")
        flash('An error occurred', 'error')
        return redirect(url_for('auth.signup_step2'))