from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, UTC
from extensions import db
from enum import Enum as PyEnum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean, DateTime, Text, func, JSON, Enum

class UserRole(str, PyEnum):
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    SOMMELIER = 'sommelier'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), nullable=False, default=UserRole.CUSTOMER.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = relationship('WineReview', back_populates='user')
    wine_interactions = relationship('UserWineInteraction', back_populates='user')
    notification_preferences = relationship(
        'UserNotificationPreference', 
        back_populates='user', 
        uselist=False,
        cascade='all, delete-orphan'
    )
    interactions_made = relationship(
        'UserInteraction', 
        foreign_keys='UserInteraction.user_id', 
        back_populates='user'
    )
    interactions_received = relationship(
        'UserInteraction', 
        foreign_keys='UserInteraction.target_user_id', 
        back_populates='target_user'
    )
    
    # Add relationship to traits
    preferred_traits = db.relationship('WineTrait', secondary=user_traits,
                                     backref=db.backref('users', lazy='dynamic'))
    is_admin = db.Column(db.Boolean, default=False)

class WineVarietal(db.Model):
    __tablename__ = 'wine_varietals'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationship with Wines
    wines = relationship('Wine', back_populates='varietal')

class WineRegion(db.Model):
    __tablename__ = 'wine_regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    country = Column(String(100))
    description = Column(Text)
    
    # Relationship with Wines
    wines = relationship('Wine', back_populates='region')

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Wine preference fields
    preferred_wine_types = db.Column(db.JSON, nullable=True)
    preferred_regions = db.Column(db.JSON, nullable=True)
    preferred_price_range = db.Column(db.JSON, nullable=True)
    
    # Flavor and style preferences
    flavor_profiles = db.Column(db.JSON, nullable=True)
    wine_styles = db.Column(db.JSON, nullable=True)
    
    # Relationship with User
    user = db.relationship('User', backref='preferences', uselist=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_wine_types': self.preferred_wine_types,
            'preferred_regions': self.preferred_regions,
            'preferred_price_range': self.preferred_price_range,
            'flavor_profiles': self.flavor_profiles,
            'wine_styles': self.wine_styles
        }
    

class Wine(db.Model):
    __tablename__ = 'wines'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # e.g., Red, White, Rose
    price = Column(Float)
    alcohol_percentage = Column(Float)
    
    # Foreign Keys
    varietal_id = Column(Integer, ForeignKey('wine_varietals.id'))
    region_id = Column(Integer, ForeignKey('wine_regions.id'))
    
    # Relationships
    varietal = relationship('WineVarietal', back_populates='wines')
    region = relationship('WineRegion', back_populates='wines')
    reviews = relationship('WineReview', back_populates='wine')
    wine_interactions = relationship('UserWineInteraction', back_populates='wine')
    user_interactions = relationship('UserInteraction', back_populates='wine')
    
    # Add relationship to traits
    traits = db.relationship('WineTrait', secondary=wine_traits,
                           backref=db.backref('wines', lazy='dynamic'))

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=True)
    
    # Interaction types
    interaction_type = db.Column(db.String(50), nullable=False)  # e.g., view, like, recommend, share
    
    # Additional metadata
    interaction_details = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], back_populates='interactions_made')
    target_user = relationship('User', foreign_keys=[target_user_id], back_populates='interactions_received')
    wine = relationship('Wine', back_populates='user_interactions')

    def to_dict(self):
        """
        Convert interaction to dictionary for easy serialization
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_user_id': self.target_user_id,
            'wine_id': self.wine_id,
            'interaction_type': self.interaction_type,
            'interaction_details': self.interaction_details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def log_interaction(
        cls, 
        user_id, 
        interaction_type, 
        target_user_id=None, 
        wine_id=None, 
        details=None
    ):
        """
        Class method to easily log interactions
        
        :param user_id: ID of the user performing the interaction
        :param interaction_type: Type of interaction
        :param target_user_id: Optional ID of the target user
        :param wine_id: Optional ID of the wine involved
        :param details: Optional additional details about the interaction
        :return: Created interaction instance
        """
        interaction = cls(
            user_id=user_id,
            target_user_id=target_user_id,
            wine_id=wine_id,
            interaction_type=interaction_type,
            interaction_details=details or {}
        )
        
        try:
            db.session.add(interaction)
            db.session.commit()
            return interaction
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to log interaction: {e}")
            return None

    @classmethod
    def get_user_interactions(
        cls, 
        user_id, 
        interaction_type=None, 
        limit=50, 
        offset=0
    ):
        """
        Retrieve user interactions with optional filtering
        
        :param user_id: ID of the user
        :param interaction_type: Optional specific interaction type
        :param limit: Number of interactions to retrieve
        :param offset: Pagination offset
        :return: List of interactions
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if interaction_type:
            query = query.filter_by(interaction_type=interaction_type)
        
        return query.order_by(cls.created_at.desc())\
                   .limit(limit)\
                   .offset(offset)\
                   .all()
    
class WineReview(db.Model):
    __tablename__ = 'wine_reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    wine_id = Column(Integer, ForeignKey('wines.id'), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='reviews')
    wine = relationship('Wine', back_populates='reviews')

class UserWineInteraction(db.Model):
    __tablename__ = 'user_wine_interactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    wine_id = Column(Integer, ForeignKey('wines.id'), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # e.g., view, like, favorite, share
    interaction_weight = Column(Float, default=1.0)  # Weight of the interaction (e.g., 1.0 for view, 2.0 for like, 3.0 for favorite)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='wine_interactions')
    wine = relationship('Wine', back_populates='wine_interactions')

class WineRestock(db.Model):
    __tablename__ = 'wine_restocks'

    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=False)
    requested_quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wine = db.relationship('Wine', backref='restock_requests')

class WineInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    min_threshold = db.Column(db.Integer, default=20)  # Add minimum threshold
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Relationship
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class NotificationType(PyEnum):
    RECOMMENDATION = 'recommendation'
    WINE_REVIEW = 'wine_review'
    COMMUNITY_POST = 'community_post'
    ORDER_STATUS = 'order_status'
    FRIEND_CONNECTION = 'friend_connection'

# models/notification.py


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  
    content = db.Column(db.Text, nullable=False)
    notification_details = db.Column(JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

class UserNotificationPreference(db.Model):
    __tablename__ = 'user_notification_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False, 
        unique=True
    )
    
    # Notification preferences
    email_connection_requests = Column(Boolean, default=True)
    email_wine_recommendations = Column(Boolean, default=True)
    email_community_updates = Column(Boolean, default=True)
    
    push_connection_requests = Column(Boolean, default=True)
    push_wine_recommendations = Column(Boolean, default=True)
    push_community_updates = Column(Boolean, default=True)
    
    # Relationship with User
    user = relationship('User', back_populates='notification_preferences')

# models/subscription.py

class SubscriptionTier(PyEnum):
    BASIC = 'basic'
    PREMIUM = 'premium'
    ELITE = 'elite'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('User', backref='subscription_transactions')
    plan = db.relationship('SubscriptionPlan')

class EventType(PyEnum):
    VIRTUAL = 'virtual'
    PHYSICAL = 'physical'
    HYBRID = 'hybrid'

class EventCategory(PyEnum):
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
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
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

# models/community.py

class PostType(PyEnum):
    REVIEW = 'review'
    DISCUSSION = 'discussion'
    RECOMMENDATION = 'recommendation'
    EVENT = 'event'

class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type = db.Column(db.Enum(PostType), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Optional references
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    
    # Media and attachments
    image_url = db.Column(db.String(300), nullable=True)
    
    # Engagement metrics
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='posts')
    wine = db.relationship('Wine', backref='community_posts')
    event = db.relationship('Event', backref='community_posts')

class PostComment(db.Model):
    __tablename__ = 'post_comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('CommunityPost', backref='comments')
    user = db.relationship('User', backref='comments')

class UserConnection(db.Model):
    __tablename__ = 'user_connections'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_connections')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_connections')



# models/cellar.py

class WineCellarStatus(PyEnum):
    IN_STOCK = 'in_stock'
    AGING = 'aging'
    CONSUMED = 'consumed'
    GIFTED = 'gifted'
    SOLD = 'sold'

class WineCellar(db.Model):
    __tablename__ = 'wine_cellars'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=False)
    
    # Inventory details
    quantity = db.Column(db.Integer, default=1)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float, nullable=True)
    
    # Wine aging and storage
    storage_location = db.Column(db.String(200), nullable=True)
    expected_peak_year = db.Column(db.Integer, nullable=True)
    
    # Status tracking
    status = db.Column(db.Enum(WineCellarStatus), default=WineCellarStatus.IN_STOCK)
    status_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tasting and consumption
    date_consumed = db.Column(db.DateTime, nullable=True)
    personal_rating = db.Column(db.Float, nullable=True)
    tasting_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='cellar_wines')
    wine = db.relationship('Wine', backref='cellar_entries')

class WineCellarTransaction(db.Model):
    __tablename__ = 'wine_cellar_transactions'

    id = db.Column(db.Integer, primary_key=True)
    cellar_id = db.Column(db.Integer, db.ForeignKey('wine_cellars.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # buy, sell, gift, consume
    
    # Transaction details
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional financial details
    price = db.Column(db.Float, nullable=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    cellar_entry = db.relationship('WineCellar', backref='transactions')
    recipient = db.relationship('User', foreign_keys=[recipient_id])

# models/education.py

class CourseCategory(PyEnum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    SOMMELIER = 'sommelier'

class CourseType(PyEnum):
    VIDEO = 'video'
    TEXT = 'text'
    INTERACTIVE = 'interactive'
    WEBINAR = 'webinar'

class WineCourse(db.Model):
    __tablename__ = 'wine_courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Course details
    category = db.Column(db.Enum(CourseCategory), nullable=False)
    course_type = db.Column(db.Enum(CourseType), nullable=False)
    
    # Content and media
    content_url = db.Column(db.String(300), nullable=False)
    thumbnail_url = db.Column(db.String(300), nullable=True)
    
    # Learning metrics
    duration_minutes = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('CourseModule', back_populates='course')
    quizzes = db.relationship('CourseQuiz', back_populates='course')

class CourseModule(db.Model):
    __tablename__ = 'course_modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    
    # Content details
    content_type = db.Column(db.String(50), nullable=False)  # video, text, audio
    content_url = db.Column(db.String(300), nullable=False)
    
    # Relationships
    course = db.relationship('WineCourse', back_populates='modules')

class CourseQuiz(db.Model):
    __tablename__ = 'course_quizzes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    passing_score = db.Column(db.Float, default=0.7)
    
    # Relationships
    course = db.relationship('WineCourse', back_populates='quizzes')
    questions = db.relationship('QuizQuestion', back_populates='quiz')

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('course_quizzes.id'), nullable=False)
    
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, true_false
    
    # Question options
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    
    # Relationships
    quiz = db.relationship('CourseQuiz', back_populates='questions')

class UserCourseProgress(db.Model):
    __tablename__ = 'user_course_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    # Progress tracking
    completed_modules = db.Column(db.JSON, default=list)
    quiz_attempts = db.Column(db.Integer, default=0)
    highest_quiz_score = db.Column(db.Float, default=0)
    is_course_completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='course_progress')
    course = db.relationship('WineCourse', backref='user_progress')

# models/education_content.py


class ContentType(PyEnum):
    ARTICLE = 'article'
    INTERACTIVE_GUIDE = 'interactive_guide'
    INFOGRAPHIC = 'infographic'
    VIDEO_TUTORIAL = 'video_tutorial'
    WINE_REGION_EXPLORATION = 'wine_region_exploration'

class WineKnowledgeContent(db.Model):
    __tablename__ = 'wine_knowledge_content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False, unique=True)
    
    # Content details
    content_type = db.Column(db.Enum(ContentType), nullable=False)
    
    # Main content fields
    summary = db.Column(db.Text, nullable=True)
    main_content = db.Column(db.Text, nullable=False)
    
    # Metadata
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    
    # Multimedia
    cover_image_url = db.Column(db.String(300), nullable=True)
    additional_media = db.Column(db.JSON, nullable=True)
    
    # Interactive elements
    interactive_data = db.Column(db.JSON, nullable=True)
    
    # Tracking and engagement
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='created_content')
    categories = db.relationship('WineContentCategory', secondary='content_categories')

class WineContentCategory(db.Model):
    __tablename__ = 'wine_content_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

class ContentCategories(db.Model):
    __tablename__ = 'content_categories'

    content_id = db.Column(db.Integer, db.ForeignKey('wine_knowledge_content.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('wine_content_categories.id'), primary_key=True)

class UserContentInteraction(db.Model):
    __tablename__ = 'user_content_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('wine_knowledge_content.id'), nullable=False)
    
    # Interaction types
    viewed = db.Column(db.Boolean, default=False)
    liked = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# models/analytics.py


class ModelPerformanceMetric(db.Model):
    __tablename__ = 'model_performance_metrics'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    
    # Performance Metrics
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    
    # Model Metadata
    model_version = db.Column(db.String(50), nullable=False)
    training_dataset_size = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Training Environment
    training_environment = db.Column(db.JSON, nullable=True)

class ModelRetrainingLog(db.Model):
    __tablename__ = 'model_retraining_logs'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    
    # Retraining Details
    status = db.Column(db.String(50), nullable=False)  # started, completed, failed
    trigger_reason = db.Column(db.String(100), nullable=True)
    
    # Performance Comparison
    previous_version = db.Column(db.String(50), nullable=True)
    new_version = db.Column(db.String(50), nullable=False)
    
    # Performance Metrics
    previous_accuracy = db.Column(db.Float, nullable=True)
    new_accuracy = db.Column(db.Float, nullable=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

# Optional: Add some utility methods
def calculate_wine_average_rating(wine_id):
    """
    Calculate average rating for a specific wine
    """
    return db.session.query(func.avg(WineReview.rating))\
        .filter(WineReview.wine_id == wine_id)\
        .scalar() or 0

def get_wine_review_count(wine_id):
    """
    Get total number of reviews for a wine
    """
    return db.session.query(func.count(WineReview.id))\
        .filter(WineReview.wine_id == wine_id)\
        .scalar() or 0

class WineTrait(db.Model):
    __tablename__ = 'wine_traits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'taste', 'body', 'aroma'
    description = db.Column(db.String(200))

# User-Trait Association Table
user_traits = db.Table('user_traits',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('trait_id', db.Integer, db.ForeignKey('wine_traits.id'), primary_key=True)
)

# Wine-Trait Association Table
wine_traits = db.Table('wine_traits_association',
    db.Column('wine_id', db.Integer, db.ForeignKey('wines.id'), primary_key=True),
    db.Column('trait_id', db.Integer, db.ForeignKey('wine_traits.id'), primary_key=True)
)