# services/order_service.py
from extensions import db
from models import Order, OrderItem, Wine, User, WineInventory
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid
import random

class OrderService:
    @classmethod
    def create_order(cls, user_id, order_items, shipping_address):
        """
        Create a new order
        """
        # Generate unique order number
        order_number = str(uuid.uuid4())[:8].upper()
        
        # Calculate total price
        total_price = sum(
            item['quantity'] * item['price'] 
            for item in order_items
        )
        
        # Create order
        order = Order(
            user_id=user_id,
            order_number=order_number,
            total_price=total_price,
            shipping_address=shipping_address,
            status='pending'
        )
        db.session.add(order)
        
        # Create order items
        for item in order_items:
            wine = Wine.query.get(item['wine_id'])
            
            # Check inventory
            inventory = WineInventory.query.filter_by(
                wine_id=wine.id
            ).first()
            
            if not inventory or inventory.quantity < item['quantity']:
                raise ValueError(f"Insufficient stock for wine {wine.name}")
            
            # Reduce inventory
            inventory.quantity -= item['quantity']
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                wine_id=wine.id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        return order

    @classmethod
    def get_user_orders(cls, user_id, status=None):
        """
        Retrieve user's orders with optional status filter
        """
        query = Order.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.all()
        
        return [
            {
                'id': order.id,
                'order_number': order.order_number,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at,
                'items': [
                    {
                        'wine_id': item.wine_id,
                        'wine_name': item.wine.name,
                        'quantity': item.quantity,
                        'price': item.price
                    } for item in order.items
                ]
            } for order in orders
        ]

    @classmethod
    def update_order_status(cls, order_id, new_status):
        """
        Update order status
        """
        order = Order.query.get(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        order.status = new_status
        db.session.commit()
        return order

    @classmethod
    def calculate_sales_analytics(cls, days=30):
        """
        Calculate sales analytics for a given period
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total sales
        total_sales = db.session.query(
            func.sum(Order.total_price).label('total_revenue'),
            func.count(Order.id).label('total_orders')
        ).filter(
            Order.created_at.between(start_date, end_date),
            Order.status != 'cancelled'
        ).first()
        
        # Sales by wine type
        sales_by_type = db.session.query(
            Wine.type,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(OrderItem, Wine.id == OrderItem.wine_id) \
         .join(Order, OrderItem.order_id == Order.id) \
         .filter(Order.created_at.between(start_date, end_date)) \
         .group_by(Wine.type).all()
        
        return {
            'total_revenue': total_sales.total_revenue or 0,
            'total_orders': total_sales.total_orders or 0,
            'sales_by_type': [
                {
                    'type': result.type,
                    'total_quantity': result.total_quantity,
                    'total_revenue': result.total_revenue
                } for result in sales_by_type
            ]
        }

    @classmethod
    def process_payment(cls, order_id, payment_method):
        """
        Process payment for an order
        """
        order = Order.query.get(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        # Simulate payment processing
        try:
            # In a real-world scenario, integrate with payment gateway
            payment_success = cls._simulate_payment_gateway(
                order.total_price, 
                payment_method
            )
            
            if payment_success:
                order.status = 'paid'
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            # Log payment failure
            db.session.rollback()
            raise ValueError(f"Payment processing failed: {str(e)}")

    @classmethod
    def _simulate_payment_gateway(cls, amount, payment_method):
        """
        Simulate payment gateway integration
        """
        # Simplified payment simulation
        # In real-world, integrate with Stripe, PayPal, etc.
        if payment_method in ['credit_card', 'debit_card', 'paypal']:
            # Simulate 90% success rate
            return random.random() < 0.9
        return False