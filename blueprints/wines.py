from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from extensions import db
from models import Wine, WineReview, WineVarietal, WineRegion, User, UserWineInteraction

from services.recommendation_service import recommendation_engine

# Create Blueprint
wines_bp = Blueprint('wines', __name__)

@wines_bp.route('/list', methods=['GET'])
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

@wines_bp.route('/details/<int:wine_id>', methods=['GET'])
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

@wines_bp.route('/recommend', methods=['GET'])
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

@wines_bp.route('/review', methods=['POST'])
@jwt_required()
def add_wine_review():
    """
    Add a review for a wine
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        wine_id = data.get('wine_id')
        rating = data.get('rating')
        comment = data.get('comment')
        
        # Validate input
        if not all([wine_id, rating]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if wine exists
        wine = Wine.query.get_or_404(wine_id)
        
        # Create review
        review = WineReview(
            user_id=user_id,
            wine_id=wine_id,
            rating=rating,
            comment=comment
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
            'review_id': review.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Wine review error: {e}")
        return jsonify({'error': 'Failed to add review'}), 500