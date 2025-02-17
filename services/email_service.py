from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_order_confirmation_email(recipient_email, order, payment_details):
    try:
        msg = Message(
            'Order Confirmation',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient_email]
        )
        
        # Construct email body
        msg.body = f"""
        Thank you for your order!

        Order Details:
        Order ID: {order.id}
        Total Amount: ${order.total_price:.2f}
        Payment Status: Completed

        Items:
        {'\n'.join([
            f"- {item.wine.name} (Qty: {item.quantity}) - ${item.price * item.quantity:.2f}" 
            for item in order.order_items
        ])}

        Payment Reference: {payment_details.id}

        Thank you for shopping with us!
        """

        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        return False