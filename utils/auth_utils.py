import secrets
import hashlib
import re
from flask import current_app
import jwt
from datetime import datetime, timedelta
import bcrypt

class AuthUtils:
    """
    Comprehensive Authentication Utility Class
    """
    
    @staticmethod
    def hash_password(password):
        """
        Securely hash a password using bcrypt
        
        :param password: Plain text password
        :return: Hashed password
        """
        # Convert password to bytes if it's a string
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify a password against its hash
        
        :param plain_password: Plain text password
        :param hashed_password: Stored hashed password
        :return: Boolean indicating password match
        """
        # Ensure inputs are in bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)

    @staticmethod
    def generate_token(user_id, token_type='access', expires_delta=None):
        """
        Generate JWT token
        
        :param user_id: User identifier
        :param token_type: Type of token (access/refresh)
        :param expires_delta: Token expiration time
        :return: JWT token
        """
        # Get secret key from app config
        secret_key = current_app.config.get('SECRET_KEY')
        
        # Set default expiration
        if expires_delta is None:
            expires_delta = timedelta(hours=2) if token_type == 'access' else timedelta(days=7)
        
        # Create payload
        payload = {
            'sub': str(user_id),
            'type': token_type,
            'exp': datetime.utcnow() + expires_delta,
            'iat': datetime.utcnow()
        }
        
        # Generate token
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """
        Decode and validate JWT token
        
        :param token: JWT token
        :return: Decoded token payload
        """
        try:
            secret_key = current_app.config.get('SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def generate_reset_token(user_id, email):
        """
        Generate a password reset token
        
        :param user_id: User identifier
        :param email: User email
        :return: Reset token
        """
        # Create a secure token with user-specific information
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        
        secret_key = current_app.config.get('SECRET_KEY')
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def validate_email(email):
        """
        Validate email format
        
        :param email: Email address to validate
        :return: Boolean indicating valid email
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def generate_secure_token(length=32):
        """
        Generate a cryptographically secure random token
        
        :param length: Length of the token
        :return: Secure random token
        """
        return secrets.token_hex(length // 2)

    @staticmethod
    def generate_otp(length=6):
        """
        Generate a One-Time Password (OTP)
        
        :param length: Length of OTP
        :return: Generated OTP
        """
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    @staticmethod
    def hash_token(token):
        """
        Create a secure hash of a token
        
        :param token: Token to hash
        :return: Hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()