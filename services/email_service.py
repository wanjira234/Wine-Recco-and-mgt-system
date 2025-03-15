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
        
        # Construct email body using triple quotes and string formatting
        msg.body = """
Thank you for your order!

Order Details:
Order ID: {order_id}
Total Amount: ${total_amount:.2f}
Payment Status: Completed

Items:
{order_items}

Payment Reference: {payment_ref}

Thank you for shopping with us!
""".format(
            order_id=order.id,
            total_amount=order.total_price,
            order_items='\n'.join([
                "- {name} (Qty: {qty}) - ${price:.2f}".format(
                    name=item.wine.name, 
                    qty=item.quantity, 
                    price=item.price * item.quantity
                ) for item in order.order_items
            ]),
            payment_ref=payment_details.id if payment_details else 'N/A'
        )

        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        return False