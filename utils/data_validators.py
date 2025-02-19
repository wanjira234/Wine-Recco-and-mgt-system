import re
from decimal import Decimal, InvalidOperation

class DataValidator:
    @staticmethod
    def validate_price(price):
        """
        Validate price input
        """
        try:
            price_decimal = Decimal(str(price))
            return price_decimal > 0
        except (TypeError, InvalidOperation):
            return False

    @staticmethod
    def validate_wine_type(wine_type):
        """
        Validate wine type
        """
        valid_types = [
            'red', 'white', 'rose', 'sparkling', 
            'dessert', 'fortified'
        ]
        return wine_type.lower() in valid_types

    @staticmethod
    def sanitize_input(input_string):
        """
        Sanitize input to prevent XSS and SQL injection
        """
        # Remove potentially dangerous characters
        return re.sub(r'[<>&\'"()]', '', input_string)

    @staticmethod
    def validate_alcohol_percentage(percentage):
        """
        Validate alcohol percentage
        """
        try:
            percentage = float(percentage)
            return 0 <= percentage <= 100
        except (TypeError, ValueError):
            return False