import re
import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from flask import current_app

class AuthUtils:
    @staticmethod
    def generate_salt():
        """
        Generate a random salt for password hashing
        """
        return secrets.token_hex(16)

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash password with optional salt
        """
        if salt is None:
            salt = AuthUtils.generate_salt()
        
        # Use SHA-256 for password hashing
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed, salt

    @staticmethod
    def verify_password(stored_password, provided_password, salt):
        """
        Verify if provided password matches stored password
        """
        hashed_provided, _ = AuthUtils.hash_password(provided_password, salt)
        return hashed_provided == stored_password

    @staticmethod
    def generate_jwt_token(user_id, email):
        """
        Generate JWT token for authentication
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(
            payload, 
            current_app.config['SECRET_KEY'], 
            algorithm='HS256'
        )

    @staticmethod
    def validate_email(email):
        """
        Validate email format
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength
        - At least 8 characters
        - Contains uppercase and lowercase letters
        - Contains at least one number
        - Contains at least one special character
        """
        if len(password) < 8:
            return False
        
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(not char.isalnum() for char in password)
        
        return has_upper and has_lower and has_digit and has_special