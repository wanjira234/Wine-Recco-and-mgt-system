# Add this to your existing file or create a new file named notification_service.py
from extensions import db, socketio, celery
from models import Notification, UserNotificationPreference, User
from flask_mail import Message
from flask import current_app
import logging

class NotificationService:
    @classmethod
    def create_notification(cls, user_id, notification_type, content, metadata=None):
        """
        Create a notification for a user
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            content=content,
            metadata=metadata or {}
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Trigger real-time notification
        cls.send_real_time_notification(user_id, notification)
        
        return notification

    @classmethod
    def send_real_time_notification(cls, user_id, notification):
        """
        Send real-time notification via WebSocket
        """
        socketio.emit('new_notification', {
            'id': notification.id,
            'type': notification.type,
            'content': notification.content,
            'created_at': notification.created_at.isoformat()
        }, room=f'user_{user_id}')

    @classmethod
    @celery.task(name='send_email_notification')
    def send_email_notification(cls, user_id, notification_type, content):
        """
        Send email notification (Celery background task)
        """
        try:
            user = User.query.get(user_id)
            preferences = user.notification_preferences
            
            # Check email preference based on notification type
            should_send_email = cls._should_send_email(preferences, notification_type)
            
            if should_send_email:
                from flask_mail import Mail
                mail = Mail(current_app)
                msg = Message(
                    f"New {notification_type.replace('_', ' ').title()} Notification",
                    recipients=[user.email],
                    body=content
                )
                mail.send(msg)
        except Exception as e:
            logging.error(f"Email notification error: {str(e)}")

    @classmethod
    def _should_send_email(cls, preferences, notification_type):
        """
        Determine if email should be sent based on user preferences
        """
        email_preference_map = {
            'connection_request': preferences.email_connection_requests,
            'wine_recommendation': preferences.email_wine_recommendations,
            'community_update': preferences.email_community_updates
        }
        
        return email_preference_map.get(notification_type, False)

    @classmethod
    def mark_notification_as_read(cls, notification_id):
        """
        Mark a specific notification as read
        """
        notification = Notification.query.get(notification_id)
        
        if notification:
            notification.is_read = True
            db.session.commit()
        
        return notification

    @classmethod
    def get_user_notifications(cls, user_id, page=1, per_page=20, unread_only=False):
        """
        Retrieve user notifications with pagination
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return {
            'notifications': [
                {
                    'id': notif.id,
                    'type': notif.type,
                    'content': notif.content,
                    'is_read': notif.is_read,
                    'created_at': notif.created_at.isoformat()
                } for notif in notifications.items
            ],
            'pagination': {
                'total_pages': notifications.pages,
                'current_page': notifications.page,
                'total_items': notifications.total
            }
        }

    @classmethod
    def update_notification_preferences(cls, user_id, preferences):
        """
        Update user notification preferences
        """
        user_prefs = UserNotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not user_prefs:
            user_prefs = UserNotificationPreference(user_id=user_id)
            db.session.add(user_prefs)
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(user_prefs, key):
                setattr(user_prefs, key, value)
        
        db.session.commit()
        return user_prefs