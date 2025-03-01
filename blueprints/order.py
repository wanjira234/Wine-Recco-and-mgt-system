# blueprints/order.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.order_service import OrderService
from services.inventory_service import InventoryService

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    """
    Create a new order
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        order = OrderService.create_order(
            user_id=user_id,
            order_items=data.get('items', []),
            shipping_address=data.get('shipping_address')
        )
        
        return jsonify({
            'message': 'Order created successfully',
            'order_number': order.order_number
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@order_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    """
    Get user's orders
    """
    user_id = get_jwt_identity()
    status = request.args.get('status')
    
    try:
        orders = OrderService.get_user_orders(
            user_id=user_id, 
            status=status
        )
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/payment/<int:order_id>', methods=['POST'])
@jwt_required()
def process_payment(order_id):
    """
    Process payment for an order
    """
    data = request.get_json()
    
    try:
        success = OrderService.process_payment(
            order_id=order_id,
            payment_method=data.get('payment_method')
        )
        
        return jsonify({
            'success': success,
            'message': 'Payment processed successfully' if success 
                       else 'Payment failed'
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400