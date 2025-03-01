from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import User, UserPreference, UserRole
from datetime import timedelta
import re
import secrets

class AuthService:
    @classmethod
    def validate_email(cls, email):
        """
        Validate email format
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @classmethod
    def validate_password(cls, password):
        """
        Validate password strength
        - At least 8 characters
        - Contains at least one uppercase, one lowercase, one number
        """
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
        
        if not re.search(r'[a-z]', password):
            return False
        
        if not re.search(r'\d', password):
            return False
        
        return True

    @classmethod
    def register_user(cls, email, password, username=None, role='customer'):
        """
        Register a new user
        """
        # Validate email and password
        if not cls.validate_email(email):
            raise ValueError("Invalid email format")
        
        if not cls.validate_password(password):
            raise ValueError("Password does not meet complexity requirements")
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create user
        try:
            user = User(
                email=email,
                password=hashed_password,
                username=username or email.split('@')[0],
                role=role
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Create default user preference
            default_preference = UserPreference(
                user_id=user.id,
                preferred_wine_types=[],
                preferred_price_range=None
            )
            db.session.add(default_preference)
            db.session.commit()
            
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Registration failed")

    @classmethod
    def login(cls, email, password):
        """
        User login with JWT token generation
        """
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Check password
        if not check_password_hash(user.password, password):
            raise ValueError("Invalid credentials")
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id, 
            expires_delta=timedelta(days=1)
        )
        refresh_token = create_refresh_token(
            identity=user.id, 
            expires_delta=timedelta(days=7)
        )
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @classmethod
    def refresh_token(cls, user_id):
        """
        Generate a new access token using refresh token
        """
        new_access_token = create_access_token(
            identity=user_id, 
            expires_delta=timedelta(days=1)
        )
        return new_access_token

    @classmethod
    def reset_password_request(cls, email):
        """
        Generate password reset token
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token with expiration
        user.reset_password_token = reset_token
        user.reset_password_expires = db.func.current_timestamp() + timedelta(hours=1)
        
        db.session.commit()
        
        # TODO: Send reset email (implement email service)
        return reset_token

    @classmethod
    def reset_password(cls, reset_token, new_password):
        """
        Reset password using reset token
        """
        # Validate password
        if not cls.validate_password(new_password):
            raise ValueError("Password does not meet complexity requirements")
        
        # Find user with valid reset token
        user = User.query.filter_by(reset_password_token=reset_token).first()
        
        if not user:
            raise ValueError("Invalid reset token")
        
        # Check token expiration
        if user.reset_password_expires < db.func.current_timestamp():
            raise ValueError("Reset token has expired")
        
        # Update password
        user.password = generate_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        
        db.session.commit()
        
        return user

    @classmethod
    def update_user_profile(cls, user_id, **kwargs):
        """
        Update user profile
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Update allowed fields
        allowed_fields = ['username', 'first_name', 'last_name']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
            
            # Special handling for email
            if field == 'email':
                if cls.validate_email(value):
                    user.email = value
                else:
                    raise ValueError("Invalid email format")
        
        db.session.commit()
        return user

    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        """
        Change user password
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Validate current password
        if not check_password_hash(user.password, old_password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        if not cls.validate_password(new_password):
            raise ValueError("New password does not meet complexity requirements")
        
        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return user

    @classmethod
    def social_login(cls, email, provider, social_id):
        """
        Handle social login (Google, Facebook, etc.)
        """
        # Find existing user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user if not exists
            user = User(
                email=email,
                username=email.split('@')[0],
                role='customer',
                social_login_provider=provider,
                social_login_id=social_id
            )
            
            db.session.add(user)
            db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id, 
            expires_delta=timedelta(days=1)
        )
        refresh_token = create_refresh_token(
            identity=user.id, 
            expires_delta=timedelta(days=7)
        )
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }