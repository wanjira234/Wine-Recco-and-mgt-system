# blueprints/cellar.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.cellar_service import CellarService

cellar_bp = Blueprint('cellar', __name__)

@cellar_bp.route('/add', methods=['POST'])
@jwt_required()
def add_wine_to_cellar():
    """
    Add a wine to user's cellar
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        cellar_entry = CellarService.add_wine_to_cellar(
            user_id, 
            data['wine_id'], 
            data
        )
        return jsonify({
            'id': cellar_entry.id,
            'message': 'Wine added to cellar'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@cellar_bp.route('/<int:cellar_id>/status', methods=['PUT'])
@jwt_required()
def update_wine_status(cellar_id):
    """
    Update wine status in cellar
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        cellar_entry = CellarService.update_wine_status(
            cellar_id, 
            data['status'], 
            data
        )
        return jsonify({
            'id': cellar_entry.id,
            'status': cellar_entry.status.value,
            'message': 'Wine status updated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@cellar_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_cellar():
    """
    Get user's cellar
    """
    user_id = get_jwt_identity()
    
    # Extract filters from query parameters
    filters = {
        'status': request.args.get('status'),
        'min_purchase_year': request.args.get('min_year', type=int),
        'max_purchase_year': request.args.get('max_year', type=int)
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        cellar_entries = CellarService.get_user_cellar(user_id, filters)
        return jsonify([
            {
                'id': entry.id,
                'wine_id': entry.wine_id,
                'wine_name': entry.wine.name,
                'quantity': entry.quantity,
                'status': entry.status.value,
                'purchase_date': entry.purchase_date.isoformat(),
                'purchase_price': entry.purchase_price
            } for entry in cellar_entries
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cellar_bp.route('/aging-recommendations', methods=['GET'])
@jwt_required()
def get_aging_recommendations():
    """
    Get recommendations for aging wines
    """
    user_id = get_jwt_identity()
    
    try:
        recommendations = CellarService.get_aging_recommendations(user_id)
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cellar_bp.route('/value-analysis', methods=['GET'])
@jwt_required()
def analyze_cellar_value():
    """
    Analyze cellar value and composition
    """
    user_id = get_jwt_identity()
    
    try:
        analysis = CellarService.analyze_cellar_value(user_id)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500