from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required
from services.auth_service import AuthService
from forms import LoginForm, RegistrationForm, SignupForm
from werkzeug.security import generate_password_hash
from models import User, WineTrait
from extensions import db
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User signup page and endpoint
    """
    form = SignupForm()
    
    # Get all traits grouped by category
    traits_by_category = {}
    traits = WineTrait.query.order_by(WineTrait.category, WineTrait.name).all()
    for trait in traits:
        if trait.category not in traits_by_category:
            traits_by_category[trait.category] = []
        traits_by_category[trait.category].append(trait)
    
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form, wine_traits=traits_by_category)
    
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('auth/signup.html', form=form, wine_traits=traits_by_category)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/signup.html', form=form, wine_traits=traits_by_category)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        # Add selected traits
        selected_traits = request.form.getlist('traits')
        if selected_traits:
            traits = WineTrait.query.filter(WineTrait.id.in_(selected_traits)).all()
            user.preferred_traits.extend(traits)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            login_user(user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account', 'error')
            return render_template('auth/signup.html', form=form, wine_traits=traits_by_category)
    
    return render_template('auth/signup.html', form=form, wine_traits=traits_by_category)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and endpoint
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout endpoint
    """
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.home'))

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