from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.recommendation_service import get_recommendation_engine
from models import Wine

recommendation_bp = Blueprint('recommendation', __name__)

def get_engine():
    """
    Get the recommendation engine instance
    """
    return get_recommendation_engine()

@recommendation_bp.route('/by-traits', methods=['GET'])
def recommend_by_traits():
    """
    Recommend wines by selected traits
    """
    # Get traits from query parameters
    traits = request.args.get('traits', '').split(',')
    top_n = request.args.get('top_n', default=10, type=int)

    try:
        engine = get_engine()
        # Get recommendations
        recommendations = engine.recommend_by_traits(
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
    top_n = request.args.get('top_n', default=5, type=int)

    try:
        engine = get_engine()
        recommendations = engine.hybrid_recommendations(
            user_id, 
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
                    'description': wine.description
                } for wine in recommended_wines
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/available-traits', methods=['GET'])
def get_available_traits():
    """
    Get list of available wine traits
    """
    try:
        engine = get_engine()
        return jsonify({
            'traits': engine.all_traits
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500