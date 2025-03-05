# blueprints/community.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.community_service import CommunityService

community_bp = Blueprint('community', __name__)

@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new community post
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        post = CommunityService.create_post(user_id, data)
        return jsonify({
            'id': post.id,
            'message': 'Post created successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    """
    Add a comment to a post
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        comment = CommunityService.add_comment(
            user_id, 
            post_id, 
            data['content']
        )
        return jsonify({
            'id': comment.id,
            'message': 'Comment added successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """
    Like a post
    """
    user_id = get_jwt_identity()
    
    try:
        post = CommunityService.like_post(user_id, post_id)
        return jsonify({
            'likes_count': post.likes_count,
            'message': 'Post liked successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/connections/request', methods=['POST'])
@jwt_required()
def send_connection_request():
    """
    Send a connection request
    """
    requester_id = get_jwt_identity()
    data = request.get_json()
    receiver_id = data['receiver_id']
    
    try:
        connection = CommunityService.send_connection_request(
            requester_id, 
            receiver_id
        )
        return jsonify({
            'id': connection.id,
            'message': 'Connection request sent'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@community_bp.route('/connections/<int:connection_id>/accept', methods=['POST'])
@jwt_required()
def accept_connection_request(connection_id):
    """
    Accept a connection request
    """
    receiver_id = get_jwt_identity()
    
    try:
        connection = CommunityService.accept_connection_request(
            connection_id, 
            receiver_id
        )
        return jsonify({
            'id': connection.id,
            'message': 'Connection request accepted'
        }), 200
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
            user_id, 
            page, 
            per_page
        )
        return jsonify(feed), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500