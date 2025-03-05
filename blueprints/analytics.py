# blueprints/analytics.py
import functools
from flask import Blueprint, jsonify
from services.analytics_service import AnalyticsService
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from models import UserRole
from extensions import cache

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

def admin_required(fn):
    """
    Custom decorator to ensure admin access
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_role = UserRole.query.filter_by(
            user_id=get_jwt_identity()
        ).first()
        
        if not user_role or user_role.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    return wrapper

@analytics_bp.route('/wine-clustering', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=3600)  # Cache for 1 hour
def wine_clustering():
    """
    Get wine clustering insights with caching
    """
    try:
        insights = analytics_service.wine_clustering()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/recommendation-insights', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=1800)  # Cache for 30 minutes
def recommendation_insights():
    """
    Get wine recommendation insights with caching
    """
    try:
        insights = analytics_service.wine_recommendation_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/price-sensitivity', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=3600)  # Cache for 1 hour
def price_sensitivity():
    """
    Analyze price sensitivity with caching
    """
    try:
        insights = analytics_service.price_sensitivity_analysis()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/comprehensive-report', methods=['GET'])
@jwt_required()
@admin_required
def comprehensive_report():
    """
    Generate comprehensive analytics report
    """
    try:
        report = analytics_service.generate_comprehensive_report()
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export-report', methods=['POST'])
@jwt_required()
@admin_required
def export_report():
    """
    Export comprehensive report
    """
    try:
        report = analytics_service.generate_comprehensive_report()
        
        # Generate export (CSV, PDF, etc.)
        export_path = generate_report_export(report)
        
        return jsonify({
            'message': 'Report exported successfully',
            'export_path': export_path
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500