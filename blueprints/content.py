# blueprints/content.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.content_service import ContentService
from models import WineContentCategory

content_bp = Blueprint('content', __name__)

@content_bp.route('/categories', methods=['GET'])
def get_content_categories():
    """
    Get available content categories
    """
    try:
        # Ensure categories exist
        ContentService.create_content_categories()
        
        categories = WineContentCategory.query.all()
        return jsonify([
            {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description
            } for cat in categories
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/list', methods=['GET'])
def get_content_list():
    """
    Get list of content with filtering
    """
    filters = {
        'content_type': request.args.get('type'),
        'categories': request.args.getlist('categories'),
        'tags': request.args.getlist('tags')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v}
    
    try:
        contents = ContentService.get_content_list(filters)
        return jsonify([
            {
                'id': content.id,
                'title': content.title,
                'slug': content.slug,
                'content_type': content.content_type.value,
                'summary': content.summary,
                'cover_image_url': content.cover_image_url,
                'views_count': content.views_count,
                'likes_count': content.likes_count,
                'categories': [cat.name for cat in content.categories]
            } for content in contents
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['GET'])
@jwt_required()
def get_content_details(content_id):
    """
    Get detailed content
    """
    user_id = get_jwt_identity()
    
    try:
        content = ContentService.get_content_details(content_id, user_id)
        return jsonify(content), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@content_bp.route('/<int:content_id>/like', methods=['POST'])
@jwt_required()
def like_content(content_id):
    """
    Like a piece of content
    """
    user_id = get_jwt_identity()
    
    try:
        likes_count = ContentService.like_content(content_id, user_id)
        return jsonify({
            'likes_count': likes_count,
            'message': 'Content liked successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400