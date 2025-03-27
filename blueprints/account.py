from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user, logout_user
from flask_jwt_extended import jwt_required, get_jwt_identity
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

@account_bp.route('/delete-profile', methods=['POST'])
@login_required
def delete_profile():
    """Delete user account"""
    try:
        # Get the current user
        user = current_user
        
        # Store username for logging
        username = user.username
        
        # Delete the account using the model method
        if user.delete_account():
            # Log the deletion
            current_app.logger.info(f"User account deleted successfully: {username}")
            
            # Log out the user and clear session
            logout_user()
            
            return jsonify({
                'success': True,
                'message': 'Account deleted successfully',
                'redirect': url_for('main.index')
            })
        else:
            current_app.logger.error(f"Failed to delete user account: {username}")
            return jsonify({
                'success': False,
                'message': 'Failed to delete account'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error deleting account: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e) if str(e) else 'An error occurred while deleting your account'
        }), 500

@account_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        # Validate required fields
        if not data.get('username'):
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        # Check if username is taken by another user
        existing_user = User.query.filter(
            User.username == data['username'],
            User.id != current_user.id
        ).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username is already taken'
            }), 400

        # Check if email is taken by another user
        existing_user = User.query.filter(
            User.email == data['email'],
            User.id != current_user.id
        ).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email is already taken'
            }), 400

        # Update user information
        current_user.username = data['username']
        current_user.email = data['email']
        
        # Update wine preferences
        if 'wine_preferences' in data and isinstance(data['wine_preferences'], dict):
            current_user.wine_preferences = {
                'wine_types': data['wine_preferences'].get('wine_types', []),
                'price_range': data['wine_preferences'].get('price_range', '')
            }
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while updating your profile'
        }), 500

@account_bp.route('/view-profile', methods=['GET'])
@login_required
def view_profile():
    """View user profile"""
    return render_template('account/profile.html')

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
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error fetching profile: {str(e)}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@account_bp.route('/profile', methods=['PUT'])
@jwt_required()
def api_update_profile():
    """API endpoint for updating user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data = request.get_json() or {}
        
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'wine_preferences' in data and data['wine_preferences'] is not None:
            user.wine_preferences = data['wine_preferences']
        if 'taste_preferences' in data and data['taste_preferences'] is not None:
            user.taste_preferences = data['taste_preferences']
        
        db.session.commit()
        return jsonify(user.to_dict())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@account_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences"""
    preferences = {
        'wine_preferences': current_user.wine_preferences or {},
        'taste_preferences': current_user.taste_preferences or {},
        'preferred_traits': [trait.to_dict() for trait in current_user.preferred_traits] if hasattr(current_user, 'preferred_traits') else []
    }
    return jsonify(preferences)

@account_bp.route('/preferences', methods=['PUT'])
@login_required
def api_update_preferences():
    """Update user preferences via API"""
    data = request.get_json()
    
    if 'wine_preferences' in data:
        current_user.wine_preferences = data['wine_preferences']
    
    if 'taste_preferences' in data:
        current_user.taste_preferences = data['taste_preferences']
    
    # Handle trait preferences if present
    if 'trait_ids' in data and hasattr(current_user, 'preferred_traits'):
        from models import WineTrait
        trait_ids = data['trait_ids']
        traits = WineTrait.query.filter(WineTrait.id.in_(trait_ids)).all()
        current_user.preferred_traits = traits
    
    db.session.commit()
    
    # Return updated preferences
    updated_preferences = {
        'wine_preferences': current_user.wine_preferences or {},
        'taste_preferences': current_user.taste_preferences or {},
        'preferred_traits': [trait.to_dict() for trait in current_user.preferred_traits] if hasattr(current_user, 'preferred_traits') else []
    }
    return jsonify(updated_preferences)

@account_bp.route('/reviews', methods=['GET'])
@login_required
def get_reviews():
    """Get user reviews"""
    try:
        reviews = WineReview.query.filter_by(user_id=current_user.id)\
            .order_by(WineReview.created_at.desc()).all()
        return jsonify([review.to_dict() for review in reviews])
    except Exception as e:
        current_app.logger.error(f"Error fetching reviews: {str(e)}")
        return jsonify({'error': 'Failed to fetch reviews'}), 500

@account_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get user orders"""
    try:
        orders = Order.query.filter_by(user_id=current_user.id)\
            .order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders])
    except Exception as e:
        current_app.logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500 