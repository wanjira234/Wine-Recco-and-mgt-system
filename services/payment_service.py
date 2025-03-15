import stripe
import os
from flask import current_app
from models import db, Order, WineInventory
from services.email_service import send_order_confirmation_email

class PaymentService:
    def __init__(self):
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    def process_payment(self, order, payment_method_id):
        try:
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Convert to cents
                currency='usd',
                payment_method=payment_method_id,
                confirm=True
            )

            # Update order status
            order.status = 'Paid'
            db.session.commit()

            return payment_intent
        except stripe.error.CardError as e:
            # Handle card errors
            current_app.logger.error(f"Card payment error: {str(e)}")
            return None

    def update_inventory(self, order):
        for item in order.order_items:
            # Find or create inventory record
            inventory = WineInventory.query.filter_by(
                wine_id=item.wine_id
            ).first()

            if inventory:
                # Reduce inventory
                inventory.quantity -= item.quantity
                if inventory.quantity < 0:
                    current_app.logger.warning(
                        f"Negative inventory for wine {item.wine_id}"
                    )
            else:
                current_app.logger.error(
                    f"No inventory record for wine {item.wine_id}"
                )

        db.session.commit()

    def complete_order(self, order, user, payment_method_id):
        try:
            # Process payment
            payment_result = self.process_payment(order, payment_method_id)
            
            if payment_result:
                # Update inventory
                self.update_inventory(order)
                
                # Send confirmation email
                send_order_confirmation_email(
                    user.email, 
                    order, 
                    payment_result
                )
                
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Order completion error: {str(e)}")
            return False