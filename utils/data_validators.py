import re
from typing import Any, Dict, List, Union
from marshmallow import Schema, ValidationError, fields, validate

class DataValidator:
    """
    Comprehensive Data Validation Utility
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        :param email: Email address to validate
        :return: Boolean indicating valid email
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength
        
        :param password: Password to validate
        :return: Boolean indicating password strength
        """
        # At least 8 characters, one uppercase, one lowercase, one number
        strength_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
        return re.match(strength_regex, password) is not None

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format
        
        :param phone: Phone number to validate
        :return: Boolean indicating valid phone number
        """
        phone_regex = r'^\+?1?\d{9,15}$'
        return re.match(phone_regex, phone) is not None

    @classmethod
    def validate_data(cls, data: Dict[str, Any], schema_definition: Dict[str, Any]) -> Union[Dict[str, Any], List[str]]:
        """
        Generic data validation using dynamic schema
        
        :param data: Data to validate
        :param schema_definition: Schema definition
        :return: Validated data or list of errors
        """
        class DynamicSchema(Schema):
            pass

        # Dynamically create schema fields
        for field_name, field_config in schema_definition.items():
            field_type = field_config.get('type', str)
            required = field_config.get('required', False)
            validators = field_config.get('validators', [])

            # Map Python types to Marshmallow fields
            field_mapping = {
                str: fields.String,
                int: fields.Integer,
                float: fields.Float,
                bool: fields.Boolean,
                list: fields.List,
                dict: fields.Dict
            }

            # Create field with appropriate validators
            field_class = field_mapping.get(field_type, fields.String)
            field_args = {
                'required': required,
                'validate': validators
            }

            setattr(DynamicSchema, field_name, field_class(**field_args))

        try:
            # Validate data
            schema = DynamicSchema()
            validated_data = schema.load(data)
            return validated_data
        except ValidationError as err:
            return err.messages

    @staticmethod
    def sanitize_input(input_data: str) -> str:
        """
        Sanitize input to prevent XSS and injection
        
        :param input_data: Input to sanitize
        :return: Sanitized input
        """
        # Remove potentially dangerous HTML tags and scripts
        return re.sub(r'<[^>]+>', '', input_data)

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format
        
        :param url: URL to validate
        :return: Boolean indicating valid URL
        """
        url_regex = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[^/\s]*)*/?$'
        return re.match(url_regex, url) is not None