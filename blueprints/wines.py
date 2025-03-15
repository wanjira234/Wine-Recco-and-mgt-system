from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Wine, WineReview
from services.recommendation_service import recommendation_engine
from sqlalchemy import func

wines_bp = Blueprint('wines', __name__)

# Existing routes remain the same as in your original implementation

@wines_bp.route('/recommendations', methods=['GET'])
@login_required
def get_wine_recommendations():
    try:
        # Get recommendations for the current user
        recommended_wine_ids = recommendation_engine.hybrid_recommendations(
            current_user.id
        )

        # Fetch wine details
        recommended_wines = Wine.query.filter(Wine.id.in_(recommended_wine_ids)).all()

        return jsonify({
            'recommendations': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'region': wine.region,
                    'price': wine.price,
                    'image_url': wine.image_url,
                    'description': wine.description
                } for wine in recommended_wines
            ]
        })
    except Exception as e:
        # Error handling
        return jsonify({"error": str(e)}), 500

@wines_bp.route('/refresh-recommendations', methods=['POST'])
@login_required
def refresh_recommendation_model():
    try:
        recommendation_engine.load_wine_data()
        return jsonify({
            "message": "Recommendation model refreshed successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to refresh recommendation model",
            "details": str(e)
        }), 500