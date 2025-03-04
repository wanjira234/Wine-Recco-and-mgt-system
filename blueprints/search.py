# blueprints/search.py
from flask import Blueprint, request, jsonify
from services.search_service import SearchService

search_bp = Blueprint('search', __name__)
search_service = SearchService()

@search_bp.route('/wines', methods=['GET'])
def search_wines():
    """
    Advanced wine search endpoint
    """
    try:
        # Extract query parameters
        query_params = {
            'q': request.args.get('q'),
            'type': request.args.get('type'),
            'price_min': request.args.get('price_min', type=float),
            'price_max': request.args.get('price_max', type=float),
            'traits': request.args.get('traits'),
            'sort': request.args.get('sort'),
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 20, type=int)
        }

        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}

        # Perform search
        results = search_service.advanced_search(query_params)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/suggest', methods=['GET'])
def suggest_wines():
    """
    Wine suggestion endpoint
    """
    query = request.args.get('q', '')
    
    try:
        suggestions = search_service.suggest_wines(query)
        return jsonify(suggestions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/index', methods=['POST'])
def index_wines():
    """
    Manually trigger wine indexing
    """
    try:
        search_service.index_wines()
        return jsonify({'message': 'Wines indexed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500