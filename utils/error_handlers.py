from flask import jsonify, current_app, render_template, request
import traceback
import logging
from functools import wraps
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError, IntegrityError

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

        # Handle Database Errors
        if isinstance(error, SQLAlchemyError):
            if isinstance(error, OperationalError):
                # Handle missing tables/columns
                if "no such table" in str(error) or "no such column" in str(error):
                    message = "Database schema is not up to date. Please run database migrations."
                    logger.error(f"Database schema error: {message}")
                    return jsonify({
                        'error': 'Database Schema Error',
                        'message': message,
                        'status_code': 500,
                        'action_required': 'Run database migrations'
                    }), 500
            elif isinstance(error, ProgrammingError):
                return jsonify({
                    'error': 'Database Programming Error',
                    'message': 'A database operation failed due to programming error',
                    'status_code': 500
                }), 500
            elif isinstance(error, IntegrityError):
                return jsonify({
                    'error': 'Database Integrity Error',
                    'message': 'The operation violated database integrity constraints',
                    'status_code': 400
                }), 400
            return jsonify({
                'error': 'Database Error',
                'message': 'A database operation failed',
                'status_code': 500
            }), 500

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
            'message': str(error),
            'status_code': 500
        }), 500

    @staticmethod
    def handle_initialization_error(error, component_name):
        """
        Handle initialization errors for application components
        
        :param error: Exception object
        :param component_name: Name of the component that failed to initialize
        :return: None, but logs the error and sets up fallback if possible
        """
        logger.error(f"{component_name} initialization failed: {str(error)}")
        logger.error(traceback.format_exc())
        
        if isinstance(error, SQLAlchemyError):
            logger.error("Database error during initialization. Please ensure database is properly configured and migrations are up to date.")
            if isinstance(error, OperationalError):
                if "no such table" in str(error) or "no such column" in str(error):
                    logger.error("Database schema is out of date. Running migrations may fix this issue.")
                    logger.error("Try running: flask db upgrade")

    @staticmethod
    def log_error(error, level=logging.ERROR):
        """
        Log an error with the specified level
        
        :param error: Exception object
        :param level: Logging level (default: ERROR)
        """
        logger.log(level, f"Error occurred: {str(error)}")
        logger.log(level, traceback.format_exc())

    @staticmethod
    def validation_error_handler(errors):
        """
        Handle validation errors
        
        :param errors: Validation errors dictionary
        :return: JSON response with validation errors
        """
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'errors': errors,
            'status_code': 400
        }), 400

    @classmethod
    def register_error_handlers(cls, app):
        """
        Register all error handlers for the application
        
        :param app: Flask application instance
        """
        @app.errorhandler(Exception)
        def handle_global_error(error):
            """Handle all unhandled exceptions"""
            if request.path.startswith('/api/'):
                return cls.handle_error(error)
            return render_template('home.html', config_data=get_base_config()), 500

        @app.errorhandler(404)
        def not_found_error(error):
            """Handle 404 Not Found errors"""
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Not Found',
                    'message': 'The requested resource was not found',
                    'status_code': 404
                }), 404
            return render_template('home.html', config_data=get_base_config()), 404

        @app.errorhandler(500)
        def internal_server_error(error):
            """Handle 500 Internal Server Error"""
            app.logger.error(f"Internal Server Error: {error}")
            return render_template('home.html', config_data=get_base_config()), 500

        @app.errorhandler(403)
        def forbidden_error(error):
            """Handle 403 Forbidden Error"""
            app.logger.error(f"Forbidden Error: {error}")
            return render_template('home.html', config_data=get_base_config()), 403

        @app.errorhandler(SQLAlchemyError)
        def handle_db_error(error):
            """Handle database-related errors"""
            return cls.handle_error(error)

def get_base_config():
    """Get base configuration for templates"""
    return {
        'apiUrl': current_app.config.get('API_URL', ''),
        'environment': current_app.config.get('ENV', 'development'),
        'debug': current_app.config.get('DEBUG', False),
        'csrfToken': generate_csrf()
    }

def request_wants_json():
    """Check if the request wants JSON response"""
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

# Export the error handler functions
register_error_handlers = ErrorHandler.register_error_handlers
handle_error = ErrorHandler.handle_error
handle_initialization_error = ErrorHandler.handle_initialization_error
log_error = ErrorHandler.log_error
validation_error_handler = ErrorHandler.validation_error_handler