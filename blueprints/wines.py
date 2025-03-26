from flask import Blueprint, jsonify, request, current_app, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user
from sqlalchemy import func, case

from extensions import db
from models import Wine, WineReview, WineVarietal, WineRegion, User, UserWineInteraction, WineTrait, wine_traits
from services.recommendation_service import recommendation_engine

# Create Blueprint
wines_bp = Blueprint('wines', __name__)

# React Routes - These serve the React application
@wines_bp.route('/wines')
def react_wines():
    """Serve the React-based wines page."""
    return render_template('react_base.html')

@wines_bp.route('/wines/<int:wine_id>')
def react_wine_detail(wine_id):
    """Serve the React-based wine detail page."""
    return render_template('react_base.html')

@wines_bp.route('/wines/new')
@jwt_required()
def react_wine_form():
    """Serve the React-based wine form page."""
    return render_template('react_base.html')

# API Endpoints - These serve the React frontend
@wines_bp.route('/api/wines', methods=['GET'])
def list_wines():
    """
    List wines with optional filtering and pagination
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtering parameters
        wine_type = request.args.get('type')
        varietal_id = request.args.get('varietal_id', type=int)
        region_id = request.args.get('region_id', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Base query
        query = Wine.query
        
        # Apply filters
        if wine_type:
            query = query.filter(Wine.type == wine_type)
        
        if varietal_id:
            query = query.filter(Wine.varietal_id == varietal_id)
        
        if region_id:
            query = query.filter(Wine.region_id == region_id)
        
        if min_price is not None:
            query = query.filter(Wine.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Wine.price <= max_price)
        
        # Paginate results
        paginated_wines = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'wines': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'varietal': wine.varietal.name if wine.varietal else 'Unknown',
                    'region': wine.region.name if wine.region else 'Unknown',
                    'price': wine.price,
                    'avg_rating': recommendation_engine._calculate_average_rating(wine)
                } for wine in paginated_wines.items
            ],
            'total': paginated_wines.total,
            'pages': paginated_wines.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine listing error: {e}")
        return jsonify({'error': 'Failed to retrieve wines'}), 500

@wines_bp.route('/api/wines/<int:wine_id>', methods=['GET'])
def get_wine_details(wine_id):
    """
    Get detailed information about a specific wine
    """
    try:
        wine = Wine.query.get_or_404(wine_id)
        
        # Fetch reviews
        reviews = WineReview.query\
            .filter_by(wine_id=wine_id)\
            .order_by(WineReview.created_at.desc())\
            .limit(10)\
            .all()
        
        return jsonify({
            'wine': {
                'id': wine.id,
                'name': wine.name,
                'type': wine.type,
                'description': wine.description,
                'varietal': wine.varietal.name if wine.varietal else 'Unknown',
                'region': wine.region.name if wine.region else 'Unknown',
                'price': wine.price,
                'alcohol_percentage': wine.alcohol_percentage,
                'avg_rating': recommendation_engine._calculate_average_rating(wine)
            },
            'reviews': [
                {
                    'id': review.id,
                    'user_name': review.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                } for review in reviews
            ]
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Wine details retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve wine details'}), 500

@wines_bp.route('/api/wines', methods=['POST'])
@jwt_required()
def create_wine():
    """
    Create a new wine
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'varietal_id', 'region_id', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new wine
        wine = Wine(
            name=data['name'],
            type=data['type'],
            varietal_id=data['varietal_id'],
            region_id=data['region_id'],
            price=data['price'],
            description=data.get('description'),
            alcohol_percentage=data.get('alcohol_percentage')
        )
        
        db.session.add(wine)
        db.session.commit()
        
        return jsonify(wine.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Wine creation error: {e}")
        return jsonify({'error': 'Failed to create wine'}), 500

@wines_bp.route('/api/wines/<int:wine_id>', methods=['PUT'])
@jwt_required()
def update_wine(wine_id):
    """
    Update an existing wine
    """
    try:
        wine = Wine.query.get_or_404(wine_id)
        data = request.get_json()
        
        # Update wine fields
        for field, value in data.items():
            if hasattr(wine, field):
                setattr(wine, field, value)
        
        db.session.commit()
        
        return jsonify(wine.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Wine update error: {e}")
        return jsonify({'error': 'Failed to update wine'}), 500

@wines_bp.route('/api/wines/<int:wine_id>', methods=['DELETE'])
@jwt_required()
def delete_wine(wine_id):
    """
    Delete a wine
    """
    try:
        wine = Wine.query.get_or_404(wine_id)
        
        db.session.delete(wine)
        db.session.commit()
        
        return jsonify({'message': 'Wine deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Wine deletion error: {e}")
        return jsonify({'error': 'Failed to delete wine'}), 500

@wines_bp.route('/api/wines/<int:wine_id>/reviews', methods=['POST'])
@jwt_required()
def add_wine_review(wine_id):
    """
    Add a review for a wine
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        wine = Wine.query.get_or_404(wine_id)
        
        # Validate input
        if not all(key in data for key in ['rating', 'comment']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create review
        review = WineReview(
            user_id=user_id,
            wine_id=wine_id,
            rating=data['rating'],
            comment=data['comment']
        )
        
        db.session.add(review)
        
        # Create/update wine interaction
        interaction = UserWineInteraction.query.filter_by(
            user_id=user_id, 
            wine_id=wine_id
        ).first()
        
        if interaction:
            interaction.interaction_weight += 1
        else:
            interaction = UserWineInteraction(
                user_id=user_id,
                wine_id=wine_id,
                interaction_weight=1
            )
            db.session.add(interaction)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review added successfully',
            'review': review.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Wine review error: {e}")
        return jsonify({'error': 'Failed to add review'}), 500

@wines_bp.route('/api/wines/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """
    Get personalized wine recommendations
    """
    try:
        user_id = get_jwt_identity()
        
        # Get recommendations
        recommendations = recommendation_engine.get_personalized_recommendations(
            user_id, 
            top_n=10
        )
        
        return jsonify({
            'recommendations': recommendations
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Recommendation retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve recommendations'}), 500