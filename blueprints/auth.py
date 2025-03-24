from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService
from forms import LoginForm, RegistrationForm, SignupForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, WineTrait
from extensions import db
from sqlalchemy import func
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        step = request.args.get('step', '1')
        traits_by_category = {}
        
        if step == '3':
            all_traits = WineTrait.query.all()
            for trait in all_traits:
                if trait.category not in traits_by_category:
                    traits_by_category[trait.category] = []
                traits_by_category[trait.category].append(trait)
        
        template_name = f'auth/signup_step{step}.html'
        return render_template(template_name, traits_by_category=traits_by_category)
    
    step = request.form.get('step', '1')
    current_app.logger.info(f"Processing signup step {step}")
    
    if step == '1':
        try:
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')
            
            current_app.logger.info(f"Step 1 data received - email: {email}, name: {name}")
            
            # Validate required fields
            if not all([email, name, password]):
                flash('All fields are required', 'error')
                return redirect(url_for('auth.signup'))
            
            # Check if email exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.signup'))
            
            # Store in session
            session['signup_data'] = {
                'email': email,
                'name': name,
                'password': password
            }
            current_app.logger.info("Step 1 data stored in session")
            
            return redirect(url_for('auth.signup', step='2'))
            
        except Exception as e:
            current_app.logger.error(f"Error in signup step 1: {str(e)}")
            flash('Error during signup. Please try again.', 'error')
            return redirect(url_for('auth.signup'))
    
    elif step == '2':
        try:
            if 'signup_data' not in session:
                current_app.logger.error("No signup data in session for step 2")
                flash('Please start from the beginning', 'error')
                return redirect(url_for('auth.signup'))
            
            wine_types = request.form.getlist('wine_types')
            current_app.logger.info(f"Step 2 wine types selected: {wine_types}")
            
            if not wine_types:
                flash('Please select at least one wine type', 'error')
                return redirect(url_for('auth.signup', step='2'))
            
            session['signup_data']['preferred_types'] = wine_types
            return redirect(url_for('auth.signup', step='3'))
            
        except Exception as e:
            current_app.logger.error(f"Error in signup step 2: {str(e)}")
            flash('Error during signup. Please try again.', 'error')
            return redirect(url_for('auth.signup', step='2'))
    
    elif step == '3':
        try:
            if 'signup_data' not in session:
                current_app.logger.error("No signup data in session for step 3")
                flash('Please start from the beginning', 'error')
                return redirect(url_for('auth.signup'))
            
            signup_data = session.get('signup_data', {})
            current_app.logger.info(f"Processing final signup step with data: {signup_data}")
            
            # Create the user
            user = User(
                username=signup_data['name'],
                email=signup_data['email']
            )
            user.set_password(signup_data['password'])
            
            # Add wine type preferences
            if 'preferred_types' in signup_data:
                user.preferred_wine_types = signup_data['preferred_types']
            
            # Add trait preferences
            trait_ids = request.form.getlist('traits')
            if trait_ids:
                traits = WineTrait.query.filter(WineTrait.id.in_(trait_ids)).all()
                user.preferred_traits.extend(traits)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"User created successfully: {user.username}")
            
            # Clear session after successful commit
            session.pop('signup_data', None)
            
            # Log the user in
            login_user(user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.welcome'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in signup step 3: {str(e)}")
            flash('Error creating account. Please try again.', 'error')
            return redirect(url_for('auth.signup'))

    return redirect(url_for('auth.signup'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and endpoint
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout endpoint
    """
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

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