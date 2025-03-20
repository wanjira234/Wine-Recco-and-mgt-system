from flask import Blueprint, jsonify, request, current_app, render_template
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

@wines_bp.route('/catalog', methods=['GET'])
def catalog():
    """
    Render the wine catalog page with filtering, pagination, and personalized recommendations
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Number of wines per page
        
        # Filtering parameters
        wine_type = request.args.get('wine_type')
        price_range = request.args.get('price_range')
        region = request.args.get('region')
        
        # Base query
        query = Wine.query
        
        # If user is logged in, prioritize wines matching their preferences
        if current_user.is_authenticated:
            # Get user's preferred traits
            user_traits = set(current_user.preferred_traits)
            
            # Join with wine traits and count matches
            query = query.outerjoin(wine_traits)\
                .outerjoin(WineTrait)\
                .group_by(Wine.id)\
                .order_by(
                    func.count(case([(WineTrait.id.in_([t.id for t in user_traits]), 1)], else_=0)).desc()
                )
        
        # Apply filters
        if wine_type:
            query = query.filter(Wine.type == wine_type)
        
        if price_range:
            if price_range == '0-20':
                query = query.filter(Wine.price <= 20)
            elif price_range == '20-50':
                query = query.filter(Wine.price > 20, Wine.price <= 50)
            elif price_range == '50-100':
                query = query.filter(Wine.price > 50, Wine.price <= 100)
            elif price_range == '100+':
                query = query.filter(Wine.price > 100)
        
        if region:
            query = query.join(WineRegion).filter(WineRegion.name.ilike(f'%{region}%'))
        
        # Get paginated results
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Get similar users' favorite wines if user is authenticated
        similar_wines = []
        if current_user.is_authenticated:
            similar_wines = recommendation_engine.get_similar_user_recommendations(
                current_user.id,
                limit=6
            )
        
        return render_template('catalog.html', 
                             wines=pagination.items,
                             pagination=pagination,
                             similar_wines=similar_wines)
    
    except Exception as e:
        current_app.logger.error(f"Catalog page error: {e}")
        return render_template('error.html', 
                             message="An error occurred while loading the catalog"), 500