# tasks.py
from celery import Celery
from extensions import mail
from flask_mail import Message

celery = Celery('notifications')

@celery.task
def send_email_notification(recipient_email, subject, body):
    """
    Send email notification via Celery
    """
    msg = Message(
        subject=subject,
        recipients=[recipient_email],
        body=body
    )
    mail.send(msg)