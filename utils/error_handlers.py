from flask import jsonify, current_app, render_template, request
import traceback
import logging
from functools import wraps
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import generate_csrf

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Centralized Error Handling Utility
    """
    
    @staticmethod
    def handle_error(error):
        """
        Generic error handler for different types of exceptions
        
        :param error: Exception object
        :return: JSON response with error details
        """
        # Log the error
        current_app.logger.error(f"Error occurred: {str(error)}")
        current_app.logger.error(traceback.format_exc())

        # Handle HTTP Exceptions
        if isinstance(error, HTTPException):
            return jsonify({
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            }), error.code

        # Handle specific known exceptions
        if isinstance(error, ValueError):
            return jsonify({
                'error': 'Validation Error',
                'message': str(error),
                'status_code': 400
            }), 400

        if isinstance(error, PermissionError):
            return jsonify({
                'error': 'Permission Denied',
                'message': str(error),
                'status_code': 403
            }), 403

        # Generic server error for unhandled exceptions
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'details': str(error),
            'status_code': 500
        }), 500

    @staticmethod
    def log_error(error, level=logging.ERROR):
        """
        Log errors with different severity levels
        
        :param error: Error message or exception
        :param level: Logging level
        """
        logger = current_app.logger if current_app else logging.getLogger(__name__)
        
        if isinstance(error, Exception):
            logger.log(level, f"Error: {str(error)}")
            logger.log(level, traceback.format_exc())
        else:
            logger.log(level, str(error))

    @staticmethod
    def validation_error_handler(errors):
        """
        Handle validation errors (e.g., from marshmallow or form validation)
        
        :param errors: Validation error details
        :return: JSON response with validation errors
        """
        return jsonify({
            'error': 'Validation Failed',
            'messages': errors,
            'status_code': 400
        }), 400

    @classmethod
    def register_error_handlers(cls, app):
        """
        Register global error handlers for a Flask application
        
        :param app: Flask application instance
        """
        @app.errorhandler(Exception)
        def handle_global_error(error):
            return cls.handle_error(error)

        @app.errorhandler(404)
        def not_found_error(error):
            """Handle 404 errors"""
            if request_wants_json():
                return jsonify({'error': 'Not found'}), 404
            return render_template('react_base.html', config_data=get_base_config()), 404

        @app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors"""
            logger.error(f"Internal error occurred: {error}")
            if request_wants_json():
                return jsonify({'error': 'Internal server error'}), 500
            return render_template('react_base.html', config_data=get_base_config()), 500
        
        @app.errorhandler(TypeError)
        def type_error(error):
            """Handle TypeError specifically for JSON serialization issues"""
            logger.error(f"TypeError occurred: {error}")
            if request_wants_json():
                return jsonify({'error': str(error)}), 500
            return render_template('react_base.html', config_data=get_base_config()), 500
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            """Handle all other exceptions"""
            current_app.logger.error(f"Unhandled exception: {str(error)}")
            current_app.logger.error(traceback.format_exc())
            if request_wants_json():
                return jsonify({
                    'error': 'Server Error',
                    'message': 'An unexpected error occurred',
                    'status_code': 500
                }), 500
            return render_template('react_base.html'), 500

# Export error handling functions
handle_error = ErrorHandler.handle_error
log_error = ErrorHandler.log_error
validation_error_handler = ErrorHandler.validation_error_handler
register_error_handlers = ErrorHandler.register_error_handlers

def get_base_config():
    """Get base configuration for templates"""
    return {
        'apiUrl': current_app.config.get('API_URL', '/api'),
        'environment': current_app.config.get('ENV', 'development'),
        'debug': current_app.config.get('DEBUG', False),
        'csrfToken': generate_csrf()
    }

def request_wants_json():
    """Check if the request prefers JSON response"""
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (best == 'application/json' and
            request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])