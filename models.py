from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, UTC
from extensions import db
from enum import Enum as PyEnum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean, DateTime, Text, func, JSON, Enum, Table
from flask import current_app

# Association tables
user_traits = Table('user_traits', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('trait_id', Integer, ForeignKey('wine_traits.id'), primary_key=True),
    extend_existing=True
)

wine_traits = Table('wine_traits_association', db.Model.metadata,
    Column('wine_id', Integer, ForeignKey('wines.id'), primary_key=True),
    Column('trait_id', Integer, ForeignKey('wine_traits.id'), primary_key=True),
    extend_existing=True
)

class WineTrait(db.Model):
    __tablename__ = 'wine_traits'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'taste', 'body', 'aroma'
    description = db.Column(db.String(200))
    
    def to_dict(self):
        """Convert trait object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description
        }

class UserRole(str, PyEnum):
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    SOMMELIER = 'sommelier'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=True)  # Make nullable for temporary storage
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    signup_step = db.Column(db.Integer, default=1)  # Track signup progress (1: basic info, 2: preferences, 3: traits)
    signup_data = db.Column(db.JSON, nullable=True)  # Store temporary signup data
    is_signup_complete = db.Column(db.Boolean, default=False)  # Track if signup is complete
    
    # Profile fields
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)
    
    # Wine preferences (JSON field to store wine types)
    wine_preferences = db.Column(db.JSON)
    
    # Taste preferences (JSON field to store traits)
    taste_preferences = db.Column(db.JSON)
    
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

    @classmethod
    def generate_unique_username(cls, name):
        """Generate a unique username from the given name"""
        # Remove special characters and spaces, convert to lowercase
        base_username = ''.join(e.lower() for e in name if e.isalnum())
        username = base_username
        counter = 1
        
        # Keep trying until we find a unique username
        while cls.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        return username

    @classmethod
    def create_temporary_user(cls, email, password, name):
        """Create a temporary user during the signup process"""
        user = cls(
            email=email,
            signup_step=1,
            is_signup_complete=False,
            signup_data={
                'name': name,
                'email': email
            }
        )
        user.set_password(password)
        return user

    def complete_signup(self):
        """Complete the signup process and create the final user"""
        if not self.signup_data:
            raise ValueError("No signup data available")

        # Generate unique username from the stored name
        if not self.username:
            self.username = self.generate_unique_username(self.signup_data.get('name', ''))

        # Set final user data
        self.is_signup_complete = True
        self.signup_step = 3
        
        # Clear temporary signup data
        temp_data = self.signup_data
        self.signup_data = None
        
        return temp_data

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_signup_data(self, step, data):
        """Update signup data for the current step"""
        if not self.signup_data:
            self.signup_data = {}
        
        self.signup_data.update(data)
        self.signup_step = step
        
        return self.signup_data

    def delete_account(self):
        """Delete the user account and all associated data"""
        try:
            # Delete all associated data
            WineReview.query.filter_by(user_id=self.id).delete()
            UserWineInteraction.query.filter_by(user_id=self.id).delete()
            UserInteraction.query.filter_by(user_id=self.id).delete()
            UserInteraction.query.filter_by(target_user_id=self.id).delete()
            
            # Delete the user
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting account: {str(e)}")
            return False
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization"""
        # Handle potential missing attributes with defaults
        wine_prefs = self.wine_preferences if self.wine_preferences is not None else {}
        taste_prefs = self.taste_preferences if self.taste_preferences is not None else {}
        
        # Format dates to ISO format strings
        created_at_str = self.created_at.isoformat() if self.created_at else None
        
        # Basic user data
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': created_at_str,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'first_name': self.first_name or "",
            'last_name': self.last_name or "",
            'bio': self.bio or "",
            'wine_preferences': wine_prefs,
            'taste_preferences': taste_prefs
        }
        
        # Add preferred traits if the relationship exists
        if hasattr(self, 'preferred_traits'):
            user_dict['preferred_traits'] = [
                {'id': trait.id, 'name': trait.name, 'category': trait.category}
                for trait in self.preferred_traits
            ]
        else:
            user_dict['preferred_traits'] = []
        
        return user_dict
    
    def __repr__(self):
        return f'<User {self.username}>'

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
    __tablename__ = 'user_preference'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    preference_type = Column(String(50), nullable=False)
    preference_value = Column(String(100), nullable=False)
    
    # Wine preference fields
    preferred_wine_types = Column(JSON, nullable=True)
    preferred_regions = Column(JSON, nullable=True)
    preferred_price_range = Column(JSON, nullable=True)
    
    # Flavor and style preferences
    flavor_profiles = Column(JSON, nullable=True)
    wine_styles = Column(JSON, nullable=True)
    
    # Relationship with User
    user = relationship('User', backref='preferences', uselist=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preference_type': self.preference_type,
            'preference_value': self.preference_value,
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
    category_id = Column(Integer, ForeignKey('wine_categories.id'))
    
    # Relationships
    varietal = relationship('WineVarietal', back_populates='wines')
    region = relationship('WineRegion', back_populates='wines')
    category = relationship('WineCategory', back_populates='wines')
    reviews = relationship('WineReview', back_populates='wine')
    wine_interactions = relationship('UserWineInteraction', back_populates='wine')
    user_interactions = relationship('UserInteraction', back_populates='wine')
    
    # Add relationship to traits
    traits = relationship('WineTrait', secondary=wine_traits,
                           backref=db.backref('wines', lazy='dynamic'))

    def to_dict(self):
        """Convert wine object to dictionary"""
        # Get traits safely
        traits_list = []
        if hasattr(self, 'traits') and self.traits is not None:
            traits_list = [{'id': t.id, 'name': t.name, 'category': t.category} for t in self.traits]
        
        # Calculate average rating
        avg_rating = 0.0
        review_count = 0
        if hasattr(self, 'reviews') and self.reviews is not None:
            reviews = list(self.reviews)  # Convert to list to avoid LazyLoad issues
            review_count = len(reviews)
            if review_count > 0:
                avg_rating = sum(r.rating for r in reviews) / review_count
        
        return {
            'id': self.id,
            'name': self.name or "",
            'description': self.description or "",
            'type': self.type or "",
            'price': float(self.price) if self.price is not None else 0.0,
            'alcohol_percentage': float(self.alcohol_percentage) if self.alcohol_percentage is not None else 0.0,
            'varietal': self.varietal.name if self.varietal else "",
            'varietal_id': self.varietal.id if self.varietal else None,
            'region': self.region.name if self.region else "",
            'region_id': self.region.id if self.region else None,
            'category': self.category.name if self.category else "",
            'category_id': self.category.id if self.category else None,
            'traits': traits_list,
            'average_rating': float(avg_rating),
            'review_count': review_count
        }

    def calculate_average_rating(self):
        """Calculate average rating for the wine"""
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    target_user_id = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    wine_id = Column(Integer, db.ForeignKey('wines.id'), nullable=True)
    
    # Interaction types
    interaction_type = Column(String(50), nullable=False)  # e.g., view, like, recommend, share
    
    # Additional metadata
    interaction_details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    
    def to_dict(self):
        """Convert review to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'wine_id': self.wine_id,
            'rating': float(self.rating) if self.rating is not None else 0.0,
            'comment': self.comment or "",
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'username': self.user.username if self.user else "",
            'wine_name': self.wine.name if self.wine else ""
        }

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

    id = Column(Integer, primary_key=True)
    wine_id = Column(Integer, db.ForeignKey('wines.id'), nullable=False)
    requested_quantity = Column(Integer, nullable=False)
    status = Column(String(50), default='pending')  # pending, approved, completed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wine = relationship('Wine', backref='restock_requests')

class WineInventory(db.Model):
    id = Column(Integer, primary_key=True)
    wine_id = Column(Integer, db.ForeignKey('wines.id'), unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    min_threshold = Column(Integer, default=20)  # Add minimum threshold
    last_updated = Column(DateTime, default=lambda: datetime.now(UTC))

class Order(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default='Pending')
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationship
    order_items = relationship('OrderItem', backref='order', lazy='dynamic')
    
    def to_dict(self):
        """Convert order to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_price': float(self.total_price) if self.total_price is not None else 0.0,
            'status': self.status or "Pending",
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, db.ForeignKey('order.id'), nullable=False)
    wine_id = Column(Integer, db.ForeignKey('wines.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Add relationship to wine
    wine = relationship('Wine')
    
    def to_dict(self):
        """Convert order item to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'wine_id': self.wine_id,
            'quantity': self.quantity,
            'price': float(self.price) if self.price is not None else 0.0,
            'wine_name': self.wine.name if self.wine else "",
            'subtotal': float(self.price * self.quantity) if (self.price is not None and self.quantity is not None) else 0.0
        }

class NotificationType(PyEnum):
    RECOMMENDATION = 'recommendation'
    WINE_REVIEW = 'wine_review'
    COMMUNITY_POST = 'community_post'
    ORDER_STATUS = 'order_status'
    FRIEND_CONNECTION = 'friend_connection'

# models/notification.py


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)  
    content = Column(Text, nullable=False)
    notification_details = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', backref='notifications')

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
    user = relationship('User', back_populates='notification_preferences', single_parent=True)

# models/subscription.py

class SubscriptionTier(PyEnum):
    BASIC = 'basic'
    PREMIUM = 'premium'
    ELITE = 'elite'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    tier = Column(db.Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.BASIC)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    payment_status = Column(String(50), nullable=True)
    
    user = relationship('User', backref='subscriptions')

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = Column(Integer, primary_key=True)
    tier = Column(db.Enum(SubscriptionTier), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    features = Column(JSON, nullable=True)

class SubscriptionTransaction(db.Model):
    __tablename__ = 'subscription_transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    
    user = relationship('User', backref='subscription_transactions')
    plan = relationship('SubscriptionPlan')

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

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Event details
    event_type = Column(db.Enum(EventType), nullable=False)
    category = Column(db.Enum(EventCategory), nullable=False)
    
    # Date and time
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Location details
    venue = Column(String(200), nullable=True)
    address = Column(String(300), nullable=True)
    virtual_link = Column(String(300), nullable=True)
    
    # Capacity and pricing
    total_capacity = Column(Integer, nullable=False)
    current_attendees = Column(Integer, default=0)
    ticket_price = Column(Float, nullable=False)
    
    # Event host and organization
    host_id = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    organization = Column(String(200), nullable=True)
    
    # Additional event metadata
    featured_wines = Column(JSON, nullable=True)
    requirements = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    host = relationship('User', backref='hosted_events')
    attendees = relationship('EventAttendee', back_populates='event')

class EventAttendee(db.Model):
    __tablename__ = 'event_attendees'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Ticket and payment details
    ticket_type = Column(String(50), nullable=False)
    payment_status = Column(String(50), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Additional attendee information
    dietary_restrictions = Column(String(200), nullable=True)
    special_requests = Column(Text, nullable=True)
    
    # Relationships
    event = relationship('Event', back_populates='attendees')
    user = relationship('User', backref='event_registrations')

# models/community.py

class PostType(PyEnum):
    REVIEW = 'review'
    DISCUSSION = 'discussion'
    RECOMMENDATION = 'recommendation'
    EVENT = 'event'

class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    post_type = Column(db.Enum(PostType), nullable=False)
    content = Column(Text, nullable=False)
    
    # Optional references
    wine_id = Column(Integer, db.ForeignKey('wines.id'), nullable=True)
    event_id = Column(Integer, db.ForeignKey('events.id'), nullable=True)
    
    # Media and attachments
    image_url = Column(String(300), nullable=True)
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='posts')
    wine = relationship('Wine', backref='community_posts')
    event = relationship('Event', backref='community_posts')

class PostComment(db.Model):
    __tablename__ = 'post_comments'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship('CommunityPost', backref='comments')
    user = relationship('User', backref='comments')

class UserConnection(db.Model):
    __tablename__ = 'user_connections'

    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = relationship('User', foreign_keys=[requester_id], backref='sent_connections')
    receiver = relationship('User', foreign_keys=[receiver_id], backref='received_connections')



# models/cellar.py

class WineCellarStatus(PyEnum):
    IN_STOCK = 'in_stock'
    AGING = 'aging'
    CONSUMED = 'consumed'
    GIFTED = 'gifted'
    SOLD = 'sold'

class WineCellar(db.Model):
    __tablename__ = 'wine_cellars'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    wine_id = Column(Integer, db.ForeignKey('wines.id'), nullable=False)
    
    # Inventory details
    quantity = Column(Integer, default=1)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    purchase_price = Column(Float, nullable=True)
    
    # Wine aging and storage
    storage_location = Column(String(200), nullable=True)
    expected_peak_year = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(db.Enum(WineCellarStatus), default=WineCellarStatus.IN_STOCK)
    status_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tasting and consumption
    date_consumed = Column(DateTime, nullable=True)
    personal_rating = Column(Float, nullable=True)
    tasting_notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship('User', backref='cellar_wines')
    wine = relationship('Wine', backref='cellar_entries')

class WineCellarTransaction(db.Model):
    __tablename__ = 'wine_cellar_transactions'

    id = Column(Integer, primary_key=True)
    cellar_id = Column(Integer, db.ForeignKey('wine_cellars.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # buy, sell, gift, consume
    
    # Transaction details
    quantity = Column(Integer, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Optional financial details
    price = Column(Float, nullable=True)
    recipient_id = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    cellar_entry = relationship('WineCellar', backref='transactions')
    recipient = relationship('User', foreign_keys=[recipient_id])

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

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Course details
    category = Column(db.Enum(CourseCategory), nullable=False)
    course_type = Column(db.Enum(CourseType), nullable=False)
    
    # Content and media
    content_url = Column(String(300), nullable=False)
    thumbnail_url = Column(String(300), nullable=True)
    
    # Learning metrics
    duration_minutes = Column(Integer, nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = relationship('CourseModule', back_populates='course')
    quizzes = relationship('CourseQuiz', back_populates='course')

class CourseModule(db.Model):
    __tablename__ = 'course_modules'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    
    # Content details
    content_type = Column(String(50), nullable=False)  # video, text, audio
    content_url = Column(String(300), nullable=False)
    
    # Relationships
    course = relationship('WineCourse', back_populates='modules')

class CourseQuiz(db.Model):
    __tablename__ = 'course_quizzes'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    passing_score = Column(Float, default=0.7)
    
    # Relationships
    course = relationship('WineCourse', back_populates='quizzes')
    questions = relationship('QuizQuestion', back_populates='quiz')

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, db.ForeignKey('course_quizzes.id'), nullable=False)
    
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false
    
    # Question options
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(200), nullable=False)
    
    # Relationships
    quiz = relationship('CourseQuiz', back_populates='questions')

class UserCourseProgress(db.Model):
    __tablename__ = 'user_course_progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, db.ForeignKey('wine_courses.id'), nullable=False)
    
    # Progress tracking
    completed_modules = Column(JSON, default=list)
    quiz_attempts = Column(Integer, default=0)
    highest_quiz_score = Column(Float, default=0)
    is_course_completed = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', backref='course_progress')
    course = relationship('WineCourse', backref='user_progress')

# models/education_content.py


class ContentType(PyEnum):
    ARTICLE = 'article'
    INTERACTIVE_GUIDE = 'interactive_guide'
    INFOGRAPHIC = 'infographic'
    VIDEO_TUTORIAL = 'video_tutorial'
    WINE_REGION_EXPLORATION = 'wine_region_exploration'

class WineKnowledgeContent(db.Model):
    __tablename__ = 'wine_knowledge_content'

    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    slug = Column(String(300), nullable=False, unique=True)
    
    # Content details
    content_type = Column(db.Enum(ContentType), nullable=False)
    
    # Main content fields
    summary = Column(Text, nullable=True)
    main_content = Column(Text, nullable=False)
    
    # Metadata
    author_id = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Multimedia
    cover_image_url = Column(String(300), nullable=True)
    additional_media = Column(JSON, nullable=True)
    
    # Interactive elements
    interactive_data = Column(JSON, nullable=True)
    
    # Tracking and engagement
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship('User', backref='created_content')
    categories = relationship('WineContentCategory', secondary='content_categories')

class WineContentCategory(db.Model):
    __tablename__ = 'wine_content_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

class ContentCategories(db.Model):
    __tablename__ = 'content_categories'

    content_id = Column(Integer, db.ForeignKey('wine_knowledge_content.id'), primary_key=True)
    category_id = Column(Integer, db.ForeignKey('wine_content_categories.id'), primary_key=True)

class UserContentInteraction(db.Model):
    __tablename__ = 'user_content_interactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, db.ForeignKey('wine_knowledge_content.id'), nullable=False)
    
    # Interaction types
    viewed = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# models/analytics.py


class ModelPerformanceMetric(db.Model):
    __tablename__ = 'model_performance_metrics'

    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False)
    
    # Performance Metrics
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    
    # Model Metadata
    model_version = Column(String(50), nullable=False)
    training_dataset_size = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Training Environment
    training_environment = Column(JSON, nullable=True)

class ModelRetrainingLog(db.Model):
    __tablename__ = 'model_retraining_logs'

    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False)
    
    # Retraining Details
    status = Column(String(50), nullable=False)  # started, completed, failed
    trigger_reason = Column(String(100), nullable=True)
    
    # Performance Comparison
    previous_version = Column(String(50), nullable=True)
    new_version = Column(String(50), nullable=False)
    
    # Performance Metrics
    previous_accuracy = Column(Float, nullable=True)
    new_accuracy = Column(Float, nullable=False)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

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

class WineCategory(db.Model):
    """Model for wine categories"""
    __tablename__ = 'wine_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wines = db.relationship('Wine', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<WineCategory {self.name}>'

    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }