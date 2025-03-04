# blueprints/subscription.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.subscription_service import SubscriptionService
from models import SubscriptionPlan

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """
    Get available subscription plans
    """
    plans = SubscriptionPlan.query.all()
    return jsonify([
        {
            'id': plan.id,
            'tier': plan.tier.value,
            'name': plan.name,
            'description': plan.description,
            'price': plan.price,
            'features': plan.features
        } for plan in plans
    ]), 200

@subscription_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """
    Subscribe to a plan
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Process payment and create subscription
        result = SubscriptionService.process_payment(
            user_id=user_id,
            plan_tier=data['tier'],
            payment_method=data['payment_method']
        )
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': {
                'tier': result['subscription'].tier.value,
                'start_date': result['subscription'].start_date.isoformat(),
                'end_date': result['subscription'].end_date.isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """
    Get user's current subscription
    """
    user_id = get_jwt_identity()
    
    try:
        subscription = SubscriptionService.get_user_subscription(user_id)
        
        if not subscription:
            return jsonify({'message': 'No active subscription'}), 404
        
        return jsonify({
            'tier': subscription.tier.value,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500