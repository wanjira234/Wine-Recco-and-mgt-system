# blueprints/wine_discovery.py
from flask import Blueprint, request, jsonify
from services.wine_discovery_service import WineDiscoveryService
from models import Wine

wine_discovery_bp = Blueprint('wine_discovery', __name__)
wine_discovery_service = WineDiscoveryService()

@wine_discovery_bp.route('/search', methods=['GET'])
def advanced_wine_search():
    """
    Advanced wine search endpoint
    """
    # Extract query parameters
    query_params = {
        'query': request.args.get('query'),
        'type': request.args.getlist('type'),
        'region': request.args.getlist('region'),
        'grape_variety': request.args.getlist('grape_variety'),
        'traits': request.args.getlist('traits'),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float)
    }

    # Remove None values
    query_params = {k: v for k, v in query_params.items() if v is not None}

    try:
        results = wine_discovery_service.advanced_search(query_params)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wine_discovery_bp.route('/suggestions/<int:wine_id>', methods=['GET'])
def get_wine_suggestions(wine_id):
    """
    Get wine suggestions based on a specific wine
    """
    try:
        suggestions = wine_discovery_service.get_wine_suggestions(wine_id)
        return jsonify(suggestions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wine_discovery_bp.route('/index-wines', methods=['POST'])
def index_all_wines():
    """
    Reindex all wines in Elasticsearch
    """
    try:
        # Create index
        wine_discovery_service.create_wine_index()
        
        # Get all wines and index
        wines = Wine.query.all()
        for wine in wines:
            wine_discovery_service.index_wine(wine)
        
        return jsonify({'message': 'Wines indexed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500