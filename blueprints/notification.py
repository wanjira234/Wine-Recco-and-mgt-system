# Add this to your blueprints or create a new file named notification.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import NotificationService

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """
    Update user notification preferences
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        preferences = NotificationService.update_notification_preferences(
            user_id=user_id,
            preferences=data
        )
        return jsonify({
            'message': 'Notification preferences updated',
            'preferences': {
                k: v for k, v in preferences.__dict__.items() 
                if not k.startswith('_')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get user notifications
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    try:
        notifications = NotificationService.get_user_notifications(
            user_id=user_id,
            page=page,
            per_page=per_page,
            unread_only=unread_only
        )
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    Mark a notification as read
    """
    try:
        notification = NotificationService.mark_notification_as_read(notification_id)
        return jsonify({
            'message': 'Notification marked as read',
            'notification_id': notification_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400