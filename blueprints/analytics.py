# blueprints/analytics.py
from flask import Blueprint, jsonify
from services.analytics_service import AnalyticsService
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from models import UserRole

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

def admin_required():
    """
    Custom decorator to ensure admin access
    """
    verify_jwt_in_request()
    user_role = UserRole.query.filter_by(
        user_id=get_jwt_identity()
    ).first()
    
    if not user_role or user_role.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

@analytics_bp.route('/wine-clustering', methods=['GET'])
@jwt_required()
def wine_clustering():
    """
    Get wine clustering insights
    """
    try:
        insights = analytics_service.wine_clustering()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/recommendation-insights', methods=['GET'])
@jwt_required()
def recommendation_insights():
    """
    Get wine recommendation insights
    """
    try:
        insights = analytics_service.wine_recommendation_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/price-sensitivity', methods=['GET'])
@jwt_required()
def price_sensitivity():
    """
    Analyze price sensitivity
    """
    try:
        insights = analytics_service.price_sensitivity_analysis()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/comprehensive-report', methods=['GET'])
@jwt_required()
def comprehensive_report():
    """
    Generate comprehensive analytics report
    """
    try:
        report = analytics_service.generate_comprehensive_report()
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500