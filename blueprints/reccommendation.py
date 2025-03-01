from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.recommendation_service import RecommendationEngine
from models import Wine

recommendation_bp = Blueprint('recommendation', __name__)
recommendation_engine = RecommendationEngine()

@recommendation_bp.route('/by-traits', methods=['GET'])
def recommend_by_traits():
    """
    Recommend wines by selected traits
    """
    # Get traits from query parameters
    traits = request.args.get('traits', '').split(',')
    top_n = request.args.get('top_n', default=10, type=int)

    try:
        # Get recommendations
        recommendations = recommendation_engine.recommend_by_traits(
            selected_traits=traits if traits[0] else None, 
            top_n=top_n
        )

        # Convert to JSON-serializable format
        rec_list = recommendations.to_dict('records')
        
        return jsonify({
            'recommendations': rec_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/personalized', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """
    Get personalized wine recommendations
    """
    user_id = get_jwt_identity()
    wine_id = request.args.get('wine_id', type=int)
    top_n = request.args.get('top_n', default=5, type=int)

    try:
        recommendations = recommendation_engine.hybrid_recommendations(
            user_id, 
            wine_id, 
            top_n
        )
        
        # Fetch full wine details
        recommended_wines = Wine.query.filter(Wine.id.in_(recommendations)).all()
        
        return jsonify({
            'recommendations': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'price': wine.price,
                    'description': wine.description,
                    'traits': wine.traits
                } for wine in recommended_wines
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500