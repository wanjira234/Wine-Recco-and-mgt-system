from extensions import db, socketio, celery
from flask_mail import Message
from flask import current_app
import logging
from datetime import datetime

class NotificationService:
    @classmethod
    def create_notification(cls, user_id, notification_type, content, notification_details=None):
        """
        Create a notification for a user
        """
        from models import Notification  # Local import to avoid circular dependency
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            content=content,
            notification_details=notification_details or {},
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(notification)
            db.session.commit()
            
            # Trigger real-time notification
            cls.send_real_time_notification(user_id, notification)
            
            return notification
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating notification: {str(e)}")
            return None

    @classmethod
    def send_real_time_notification(cls, user_id, notification):
        """
        Send real-time notification via WebSocket
        """
        try:
            socketio.emit('new_notification', {
                'id': notification.id,
                'type': notification.type,
                'content': notification.content,
                'created_at': notification.created_at.isoformat()
            }, room=f'user_{user_id}')
        except Exception as e:
            logging.error(f"WebSocket notification error: {str(e)}")

    @classmethod
    @celery.task(name='send_email_notification')
    def send_email_notification(cls, user_id, notification_type, content):
        """
        Send email notification (Celery background task)
        """
        from models import User, UserNotificationPreference  # Local import
        
        try:
            user = User.query.get(user_id)
            if not user:
                return
            
            # Check email preference
            preferences = user.notification_preferences
            
            if cls._should_send_email(preferences, notification_type):
                mail = current_app.extensions['mail']
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
    def mark_notification_as_read(cls, notification_id, user_id):
        """
        Mark a specific notification as read
        """
        from models import Notification  # Local import
        
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if notification:
                notification.is_read = True
                db.session.commit()
            
            return notification
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error marking notification as read: {str(e)}")
            return None

    @classmethod
    def get_user_notifications(cls, user_id, page=1, per_page=20, unread_only=False):
        """
        Retrieve user notifications with pagination
        """
        from models import Notification  # Local import
        
        try:
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
        except Exception as e:
            logging.error(f"Error retrieving notifications: {str(e)}")
            return {'notifications': [], 'pagination': {}}

    @classmethod
    def update_notification_preferences(cls, user_id, preferences):
        """
        Update user notification preferences
        """
        from models import UserNotificationPreference  # Local import
        
        try:
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
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating notification preferences: {str(e)}")
            return None