from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.wine_discovery_service import wine_discovery_service
from models import Wine, User
from extensions import db

wine_discovery_bp = Blueprint('wine_discovery', __name__)

@wine_discovery_bp.route('/search', methods=['GET'])
def advanced_wine_search():
    """
    Advanced wine search endpoint with comprehensive filtering
    """
    try:
        # Extract and validate query parameters
        query_params = {
            'query': request.args.get('query'),
            'type': request.args.getlist('type'),
            'region': request.args.getlist('region'),
            'grape_variety': request.args.getlist('grape_variety'),
            'traits': request.args.getlist('traits'),
            'min_price': request.args.get('min_price', type=float),
            'max_price': request.args.get('max_price', type=float),
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 20, type=int)
        }

        # Remove None values and validate pagination
        query_params = {k: v for k, v in query_params.items() if v is not None}
        query_params['page'] = max(1, query_params.get('page', 1))
        query_params['per_page'] = min(100, max(1, query_params.get('per_page', 20)))

        # Perform search
        results = wine_discovery_service.advanced_search(query_params)
        
        return jsonify({
            'total_results': results.get('total', 0),
            'page': query_params['page'],
            'per_page': query_params['per_page'],
            'wines': results.get('wines', [])
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine search error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during wine search',
            'details': str(e)
        }), 500

@wine_discovery_bp.route('/suggestions/<int:wine_id>', methods=['GET'])
def get_wine_suggestions(wine_id):
    """
    Get wine suggestions based on a specific wine with personalization
    """
    try:
        # Optional user-based personalization
        user_id = None
        if request.args.get('personalized', type=bool):
            user_id = get_jwt_identity()

        # Get suggestions
        suggestions = wine_discovery_service.get_wine_suggestions(
            wine_id, 
            user_id=user_id
        )
        
        return jsonify(suggestions), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine suggestions error: {str(e)}")
        return jsonify({
            'error': 'An error occurred while fetching wine suggestions',
            'details': str(e)
        }), 500

@wine_discovery_bp.route('/index-wines', methods=['POST'])
@jwt_required()  # Ensure only authenticated users can trigger
def index_all_wines():
    """
    Reindex all wines in Elasticsearch with admin-only access
    """
    try:
        # Check if user is admin
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.is_admin:
            return jsonify({
                'error': 'Unauthorized. Admin access required.'
            }), 403

        # Create index
        wine_discovery_service.create_wine_index()
        
        # Get all wines and index
        wines = Wine.query.all()
        indexed_count = 0
        
        for wine in wines:
            if wine_discovery_service.index_wine(wine):
                indexed_count += 1
        
        return jsonify({
            'message': f'Wines indexed successfully',
            'total_wines': len(wines),
            'indexed_wines': indexed_count
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine indexing error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during wine indexing',
            'details': str(e)
        }), 500

@wine_discovery_bp.route('/wine-filters', methods=['GET'])
def get_wine_filters():
    """
    Get available filters for wine discovery
    """
    try:
        filters = wine_discovery_service.get_wine_filters()
        return jsonify(filters), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine filters error: {str(e)}")
        return jsonify({
            'error': 'An error occurred while fetching wine filters',
            'details': str(e)
        }), 500