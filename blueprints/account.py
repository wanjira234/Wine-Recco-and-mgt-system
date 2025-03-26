from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import User, WineTrait, WineReview, Order
from extensions import db

account_bp = Blueprint('account', __name__)

@account_bp.route('/my-account')
@login_required
def my_account():
    """
    Display user's account dashboard
    """
    # Get user's reviews
    reviews = WineReview.query.filter_by(user_id=current_user.id)\
        .order_by(WineReview.created_at.desc()).all()
    
    # Get user's orders
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()
    
    # Get all traits grouped by category
    traits_by_category = {}
    traits = WineTrait.query.order_by(WineTrait.category, WineTrait.name).all()
    for trait in traits:
        if trait.category not in traits_by_category:
            traits_by_category[trait.category] = []
        traits_by_category[trait.category].append(trait)
    
    return render_template('account/my_account.html',
                         user=current_user,
                         reviews=reviews,
                         orders=orders,
                         wine_traits=traits_by_category)

@account_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """
    Update user's profile information
    """
    try:
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile', 'error')
    
    return redirect(url_for('account.my_account'))

@account_bp.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    """
    Update user's wine preferences
    """
    try:
        # Clear existing preferences
        current_user.preferred_traits = []
        
        # Add new preferences
        selected_traits = request.form.getlist('traits')
        if selected_traits:
            traits = WineTrait.query.filter(WineTrait.id.in_(selected_traits)).all()
            current_user.preferred_traits.extend(traits)
        
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update preferences', 'error')
    
    return redirect(url_for('account.my_account'))

@account_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile"""
    return jsonify(current_user.to_dict())

@account_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json()
    
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    if 'email' in data:
        current_user.email = data['email']
        
    db.session.commit()
    return jsonify(current_user.to_dict())

@account_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences"""
    return jsonify(current_user.preferences)

@account_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Update user preferences"""
    data = request.get_json()
    current_user.preferences = data
    db.session.commit()
    return jsonify(current_user.preferences) 