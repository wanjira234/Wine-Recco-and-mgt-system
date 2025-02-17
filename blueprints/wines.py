from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Wine, WineReview, WineInventory
from forms import ReviewForm
from sqlalchemy import func
from services.recommendation_service import WineRecommendationEngine


wines_bp = Blueprint('wines', __name__)

# Initialize the recommendation engine
recommendation_engine = WineRecommendationEngine()

# Prepare the recommendation model (you might want to do this during app initialization)
recommendation_engine.prepare_collaborative_filtering_data()

@wines_bp.route('/', methods=['GET'])
def get_wines():
    # Pagination and filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    wine_type = request.args.get('type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    region = request.args.get('region')

    # Base query
    query = Wine.query

    # Apply filters
    if wine_type:
        query = query.filter(Wine.type == wine_type)
    
    if min_price is not None:
        query = query.filter(Wine.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Wine.price <= max_price)
    
    if region:
        query = query.filter(Wine.region.ilike(f'%{region}%'))

    # Paginate results
    paginated_wines = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'wines': [
            {
                'id': wine.id,
                'name': wine.name,
                'type': wine.type,
                'region': wine.region,
                'price': wine.price,
                'image_url': wine.image_url
            } for wine in paginated_wines.items
        ],
        'total_pages': paginated_wines.pages,
        'current_page': page
    })

@wines_bp.route('/<int:wine_id>', methods=['GET'])
def get_wine_details(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    
    # Get average rating
    avg_rating = db.session.query(
        func.avg(WineReview.rating)
    ).filter(WineReview.wine_id == wine_id).scalar() or 0

    # Get recent reviews
    recent_reviews = WineReview.query.filter_by(wine_id=wine_id)\
        .order_by(WineReview.created_at.desc())\
        .limit(5).all()

    return jsonify({
        'wine': {
            'id': wine.id,
            'name': wine.name,
            'type': wine.type,
            'region': wine.region,
            'vintage': wine.vintage,
            'price': wine.price,
            'description': wine.description,
            'image_url': wine.image_url,
            'alcohol_percentage': wine.alcohol_percentage
        },
        'average_rating': round(avg_rating, 2),
        'reviews': [
            {
                'id': review.id,
                'user_id': review.user_id,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            } for review in recent_reviews
        ]
    })

@wines_bp.route('/<int:wine_id>/review', methods=['POST'])
@login_required
def add_wine_review(wine_id):
    form = ReviewForm(request.form)
    
    if form.validate():
        # Check if wine exists
        wine = Wine.query.get_or_404(wine_id)
        
        # Check if user has already reviewed this wine
        existing_review = WineReview.query.filter_by(
            user_id=current_user.id, 
            wine_id=wine_id
        ).first()
        
        if existing_review:
            return jsonify({"error": "You have already reviewed this wine"}), 400

        # Create new review
        review = WineReview(
            user_id=current_user.id,
            wine_id=wine_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        db.session.commit()

        return jsonify({
            "message": "Review added successfully",
            "review": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment
            }
        }), 201
    
    return jsonify({"errors": form.errors}), 400

@wines_bp.route('/recommendations', methods=['GET'])
@login_required
def get_wine_recommendations():
    try:
        # Use the hybrid recommendation method
        recommended_wine_ids = recommendation_engine.hybrid_recommendation(
            current_user.id
        )

        # Fetch full wine details for recommended wines
        recommended_wines = Wine.query.filter(
            Wine.id.in_(recommended_wine_ids)
        ).all()

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
        # Fallback to basic recommendation if hybrid fails
        recent_reviews = WineReview.query.filter_by(
            user_id=current_user.id
        ).order_by(WineReview.created_at.desc()).limit(5).all()

        # Get wine types from recent reviews
        reviewed_wine_types = set(
            review.wine.type for review in recent_reviews
        )

        # Find similar wines based on types and high ratings
        recommendations = Wine.query.filter(
            Wine.type.in_(reviewed_wine_types)
        ).order_by(func.random()).limit(10).all()

        return jsonify({
            'recommendations': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'region': wine.region,
                    'price': wine.price,
                    'image_url': wine.image_url
                } for wine in recommendations
            ]
        })

# Optional: Route to refresh recommendation model
@wines_bp.route('/refresh-recommendations', methods=['POST'])
@login_required
def refresh_recommendation_model():
    try:
        recommendation_engine.prepare_collaborative_filtering_data()
        return jsonify({
            "message": "Recommendation model refreshed successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to refresh recommendation model",
            "details": str(e)
        }), 500