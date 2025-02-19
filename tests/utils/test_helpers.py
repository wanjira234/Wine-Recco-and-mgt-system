import random
import string
import jwt
import datetime
from typing import Dict, Any, Optional

class TestHelpers:
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """
        Generate a random string of specified length
        
        Args:
            length (int): Length of the random string. Defaults to 10.
        
        Returns:
            str: Randomly generated string
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_random_email() -> str:
        """
        Generate a random email address
        
        Returns:
            str: Randomly generated email address
        """
        username = TestHelpers.generate_random_string(8)
        domain = TestHelpers.generate_random_string(5)
        return f"{username}@{domain}.com"

    @staticmethod
    def generate_test_user_data() -> Dict[str, str]:
        """
        Generate comprehensive test user registration data
        
        Returns:
            Dict[str, str]: Dictionary with user registration details
        """
        password = TestHelpers.generate_random_string(12)
        return {
            'username': TestHelpers.generate_random_string(8),
            'email': TestHelpers.generate_random_email(),
            'password': password,
            'confirm_password': password
        }

    @staticmethod
    def generate_mock_jwt_token(
        user_id: int, 
        secret_key: str = 'test_secret_key', 
        expiration: Optional[int] = None
    ) -> str:
        """
        Generate a mock JWT token for testing
        
        Args:
            user_id (int): User ID to encode in token
            secret_key (str): Secret key for token generation
            expiration (Optional[int]): Token expiration time in minutes
        
        Returns:
            str: Generated JWT token
        """
        if expiration is None:
            expiration = 60  # Default 1 hour
        
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration)
        }
        
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def generate_mock_wine_data() -> Dict[str, Any]:
        """
        Generate mock wine data for testing
        
        Returns:
            Dict[str, Any]: Dictionary with wine details
        """
        wine_varieties = [
            'Cabernet Sauvignon', 'Merlot', 'Pinot Noir', 
            'Chardonnay', 'Sauvignon Blanc', 'Riesling'
        ]
        
        return {
            'name': f"{TestHelpers.generate_random_string(6)} Wine",
            'variety': random.choice(wine_varieties),
            'price': round(random.uniform(10.0, 200.0), 2),
            'year': random.randint(2010, 2023),
            'description': f"A delightful wine with {TestHelpers.generate_random_string(20)} notes",
            'alcohol_percentage': round(random.uniform(10.0, 15.0), 2),
            'country': random.choice(['France', 'Italy', 'Spain', 'USA', 'Argentina', 'Chile'])
        }

    @staticmethod
    def generate_mock_recommendation_data(count: int = 5) -> list:
        """
        Generate mock recommendation data
        
        Args:
            count (int): Number of recommendations to generate
        
        Returns:
            list: List of mock wine recommendations
        """
        return [TestHelpers.generate_mock_wine_data() for _ in range(count)]

    @staticmethod
    def validate_jwt_token(
        token: str, 
        secret_key: str = 'test_secret_key'
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token
        
        Args:
            token (str): JWT token to validate
            secret_key (str): Secret key for token validation
        
        Returns:
            Optional[Dict[str, Any]]: Decoded token payload or None
        """
        try:
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Convenience import for direct use
generate_random_string = TestHelpers.generate_random_string
generate_random_email = TestHelpers.generate_random_email
generate_test_user_data = TestHelpers.generate_test_user_data
generate_mock_jwt_token = TestHelpers.generate_mock_jwt_token
generate_mock_wine_data = TestHelpers.generate_mock_wine_data
generate_mock_recommendation_data = TestHelpers.generate_mock_recommendation_data
validate_jwt_token = TestHelpers.validate_jwt_token