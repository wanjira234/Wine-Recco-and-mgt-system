from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, UTC
from extensions import db
from enum import Enum
from extensions import db
from datetime import datetime, timedelta


db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    reviews = db.relationship('WineReview', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    vintage = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    alcohol_percentage = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    
    # Relationships
    reviews = db.relationship('WineReview', backref='wine', lazy='dynamic')
    inventory = db.relationship('WineInventory', backref='wine', uselist=False)

class WineReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class WineInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Relationship
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)



class NotificationType(Enum):
    RECOMMENDATION = 'recommendation'
    WINE_REVIEW = 'wine_review'
    COMMUNITY_POST = 'community_post'
    ORDER_STATUS = 'order_status'
    FRIEND_CONNECTION = 'friend_connection'

# models/notification.py
from extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'connection', 'review', 'recommendation'
    content = db.Column(db.Text, nullable=False)
    metadata = db.Column(JSONB, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

class UserNotificationPreference(db.Model):
    __tablename__ = 'user_notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Email notification preferences
    email_connection_requests = db.Column(db.Boolean, default=True)
    email_wine_recommendations = db.Column(db.Boolean, default=True)
    email_community_updates = db.Column(db.Boolean, default=True)
    
    # Push notification preferences
    push_connection_requests = db.Column(db.Boolean, default=True)
    push_wine_recommendations = db.Column(db.Boolean, default=True)
    push_community_updates = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='notification_preferences')

# models/subscription.py

class SubscriptionTier(Enum):
    BASIC = 'basic'
    PREMIUM = 'premium'
    ELITE = 'elite'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tier = db.Column(db.Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.BASIC)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    payment_status = db.Column(db.String(50), nullable=True)
    
    user = db.relationship('User', backref='subscriptions')

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.Enum(SubscriptionTier), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    features = db.Column(db.JSON, nullable=True)

class SubscriptionTransaction(db.Model):
    __tablename__ = 'subscription_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('User', backref='subscription_transactions')
    plan = db.relationship('SubscriptionPlan')

class EventType(Enum):
    VIRTUAL = 'virtual'
    PHYSICAL = 'physical'
    HYBRID = 'hybrid'

class EventCategory(Enum):
    WINE_TASTING = 'wine_tasting'
    WINE_PAIRING = 'wine_pairing'
    SOMMELIER_WORKSHOP = 'sommelier_workshop'
    VINEYARD_TOUR = 'vineyard_tour'

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Event details
    event_type = db.Column(db.Enum(EventType), nullable=False)
    category = db.Column(db.Enum(EventCategory), nullable=False)
    
    # Date and time
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Location details
    venue = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    virtual_link = db.Column(db.String(300), nullable=True)
    
    # Capacity and pricing
    total_capacity = db.Column(db.Integer, nullable=False)
    current_attendees = db.Column(db.Integer, default=0)
    ticket_price = db.Column(db.Float, nullable=False)
    
    # Event host and organization
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    
    # Additional event metadata
    featured_wines = db.Column(db.JSON, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    host = db.relationship('User', backref='hosted_events')
    attendees = db.relationship('EventAttendee', back_populates='event')

class EventAttendee(db.Model):
    __tablename__ = 'event_attendees'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Ticket and payment details
    ticket_type = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional attendee information
    dietary_restrictions = db.Column(db.String(200), nullable=True)
    special_requests = db.Column(db.Text, nullable=True)
    
    # Relationships
    event = db.relationship('Event', back_populates='attendees')
    user = db.relationship('User', backref='event_registrations')