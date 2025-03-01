from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    """
    data = request.get_json()
    
    try:
        user = AuthService.register_user(
            email=data.get('email'),
            password=data.get('password'),
            username=data.get('username')
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    """
    data = request.get_json()
    
    try:
        login_result = AuthService.login(
            email=data.get('email'),
            password=data.get('password')
        )
        return jsonify(login_result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401

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