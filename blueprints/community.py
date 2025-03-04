# blueprints/community.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.community_service import CommunityService

community_bp = Blueprint('community', __name__)

@community_bp.route('/post', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new community post
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        post = CommunityService.create_post(
            user_id=user_id,
            content=data.get('content'),
            wine_id=data.get('wine_id'),
            image_url=data.get('image_url')
        )
        
        return jsonify({
            'message': 'Post created successfully',
            'post_id': post.id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_community_feed():
    """
    Get community feed
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        feed = CommunityService.get_community_feed(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        return jsonify(feed), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/connect/<int:target_user_id>', methods=['POST'])
@jwt_required()
def connect_users(target_user_id):
    """
    Connect with another user
    """
    user_id = get_jwt_identity()
    
    try:
        connection = CommunityService.connect_users(
            user_id=user_id,
            target_user_id=target_user_id
        )
        return jsonify({
            'message': 'Connection request sent/accepted',
            'status': connection.status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/connections', methods=['GET'])
@jwt_required()
def get_user_connections():
    """
    Get user's connections
    """
    user_id = get_jwt_identity()
    status = request.args.get('status', 'accepted')
    
    try:
        connections = CommunityService.get_user_connections(
            user_id=user_id,
            status=status
        )
        return jsonify(connections), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/wine/<int:wine_id>/social-insights', methods=['GET'])
def get_wine_social_insights(wine_id):
    """
    Get social insights for a wine
    """
    try:
        insights = CommunityService.get_wine_social_insights(wine_id)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500