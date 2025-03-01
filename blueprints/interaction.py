# blueprints/interaction.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.interaction_service import UserInteractionService
from services.review_service import WineReviewService

interaction_bp = Blueprint('interaction', __name__)

@interaction_bp.route('/view-wine/<int:wine_id>', methods=['POST'])
@jwt_required()
def log_wine_view(wine_id):
    """
    Log wine view interaction
    """
    user_id = get_jwt_identity()
    try:
        interaction = UserInteractionService.log_wine_view(user_id, wine_id)
        return jsonify({'message': 'Wine view logged'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@interaction_bp.route('/favorite-wine/<int:wine_id>', methods=['POST'])
@jwt_required()
def favorite_wine(wine_id):
    """
    Favorite a wine
    """
    user_id = get_jwt_identity()
    try:
        interaction = UserInteractionService.log_wine_favorite(user_id, wine_id)
        return jsonify({'message': 'Wine favorited'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@interaction_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """
    Get user's favorite wines
    """
    user_id = get_jwt_identity()
    try:
        favorites = UserInteractionService.get_user_favorite_wines(user_id)
        return jsonify({
            'favorites': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'price': wine.price
                } for wine in favorites
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@interaction_bp.route('/review', methods=['POST'])
@jwt_required()
def create_review():
    """
    Create a wine review
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        review = WineReviewService.create_review(
            user_id=user_id,
            wine_id=data.get('wine_id'),
            rating=data.get('rating'),
            comment=data.get('comment')
        )
        return jsonify({'message': 'Review created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@interaction_bp.route('/wine/<int:wine_id>/reviews', methods=['GET'])
def get_wine_reviews(wine_id):
    """
    Get reviews for a specific wine
    """
    try:
        reviews = WineReviewService.get_wine_reviews(wine_id)
        return jsonify({
            'reviews': [
                {
                    'user_id': review.user_id,
                    'rating': review.rating,
                    'comment': review.comment
                } for review in reviews
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400