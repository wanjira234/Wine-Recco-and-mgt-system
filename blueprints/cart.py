from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Wine, Order, OrderItem
from services.payment_service import PaymentService

cart_bp = Blueprint('cart', __name__)

# Create a function to get the payment service instance
def get_payment_service():
    if not hasattr(current_app, 'payment_service'):
        current_app.payment_service = PaymentService()
    return current_app.payment_service

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    payment_method_id = data.get('payment_method_id')

    # Get pending order
    order = Order.query.filter_by(
        user_id=current_user.id, 
        status='Pending'
    ).first()

    if not order or not order.order_items:
        return jsonify({"error": "Cart is empty"}), 400

    try:
        # Get payment service instance
        payment_service = get_payment_service()
        
        # Complete order processing
        order_completed = payment_service.complete_order(
            order, 
            current_user, 
            payment_method_id
        )

        if order_completed:
            return jsonify({
                "message": "Order completed successfully",
                "order_id": order.id,
                "total_price": order.total_price
            }), 200
        else:
            return jsonify({"error": "Payment processing failed"}), 400

    except Exception as e:
        current_app.logger.error(f"Checkout error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500