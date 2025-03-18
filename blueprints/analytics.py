from flask import Blueprint, jsonify, request
from extensions import cache, db
from models import Wine, UserInteraction, WineReview
from sqlalchemy import func, desc
import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/top-wines', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_top_wines():
    """
    Retrieve top wines based on various metrics
    """
    try:
        # Top wines by views
        top_viewed_wines = db.session.query(
            Wine, 
            func.count(UserInteraction.id).label('view_count')
        ).join(
            UserInteraction, 
            UserInteraction.wine_id == Wine.id
        ).filter(
            UserInteraction.interaction_type == 'view'
        ).group_by(Wine.id).order_by(
            desc('view_count')
        ).limit(10).all()

        # Top wines by ratings
        top_rated_wines = db.session.query(
            Wine, 
            func.avg(WineReview.rating).label('avg_rating')
        ).join(
            WineReview, 
            WineReview.wine_id == Wine.id
        ).group_by(Wine.id).order_by(
            desc('avg_rating')
        ).limit(10).all()

        # Prepare response
        response = {
            'top_viewed_wines': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'view_count': view_count
                } for wine, view_count in top_viewed_wines
            ],
            'top_rated_wines': [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'avg_rating': float(avg_rating)
                } for wine, avg_rating in top_rated_wines
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve top wines',
            'details': str(e)
        }), 500

@analytics_bp.route('/interaction-trends', methods=['GET'])
@cache.memoize(timeout=300)  # Memoized caching with dynamic key
def get_interaction_trends():
    """
    Retrieve interaction trends over time
    """
    try:
        # Interaction trends by type
        interaction_trends = db.session.query(
            UserInteraction.interaction_type,
            func.date_trunc('day', UserInteraction.created_at).label('interaction_date'),
            func.count(UserInteraction.id).label('interaction_count')
        ).group_by(
            UserInteraction.interaction_type, 
            'interaction_date'
        ).order_by(
            'interaction_date'
        ).limit(30).all()

        # Prepare response
        response = {
            'interaction_trends': [
                {
                    'type': interaction_type,
                    'date': str(interaction_date),
                    'count': interaction_count
                } for interaction_type, interaction_date, interaction_count in interaction_trends
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve interaction trends',
            'details': str(e)
        }), 500