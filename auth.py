from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """First step of signup process"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        # Validation
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.signup'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.signup'))
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('auth.signup'))
            
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.signup'))
            
        # Store user data in session for next step
        session['signup_data'] = {
            'full_name': full_name,
            'email': email,
            'password': password
        }
        
        return redirect(url_for('auth.signup_step2'))
            
    return render_template('signup/step1.html')

@auth.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    """Second step of signup process"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # Check if user data exists in session
    if 'signup_data' not in session:
        return redirect(url_for('auth.signup'))
        
    if request.method == 'POST':
        # Get form data
        wine_types = request.form.getlist('wineTypes')
        experience_level = request.form.get('experienceLevel')
        price_range = request.form.get('priceRange')
        regions = request.form.getlist('regions')
        
        # Store preferences in session
        session['signup_data'].update({
            'wine_types': wine_types,
            'experience_level': experience_level,
            'price_range': price_range,
            'regions': regions
        })
        
        return redirect(url_for('auth.signup_step3'))
        
    return render_template('signup/step2.html')

@auth.route('/signup/step3', methods=['GET', 'POST'])
def signup_step3():
    """Third step of signup process"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # Check if user data exists in session
    if 'signup_data' not in session:
        return redirect(url_for('auth.signup'))
        
    if request.method == 'POST':
        # Get form data
        body = request.form.get('body')
        flavors = request.form.getlist('flavors')
        acidity = request.form.get('acidity')
        tannin = request.form.get('tannin')
        sweetness = request.form.get('sweetness')
        
        # Store taste profile in session
        session['signup_data'].update({
            'body': body,
            'flavors': flavors,
            'acidity': acidity,
            'tannin': tannin,
            'sweetness': sweetness
        })
        
        # Create new user
        try:
            new_user = User(
                username=session['signup_data']['email'].split('@')[0],  # Use email prefix as username
                email=session['signup_data']['email'],
                full_name=session['signup_data']['full_name'],
                wine_preferences={
                    'wine_types': session['signup_data']['wine_types'],
                    'experience_level': session['signup_data']['experience_level'],
                    'price_range': session['signup_data']['price_range'],
                    'regions': session['signup_data']['regions']
                },
                taste_profile={
                    'body': session['signup_data']['body'],
                    'flavors': session['signup_data']['flavors'],
                    'acidity': session['signup_data']['acidity'],
                    'tannin': session['signup_data']['tannin'],
                    'sweetness': session['signup_data']['sweetness']
                }
            )
            new_user.set_password(session['signup_data']['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            # Clear signup data from session
            session.pop('signup_data', None)
            
            # Log in the new user
            login_user(new_user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')
            return redirect(url_for('auth.signup'))
            
    return render_template('signup/step3.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index')) 