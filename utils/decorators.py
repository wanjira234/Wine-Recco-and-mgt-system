from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User
import time
import logging

class Decorators:
    """
    Centralized Decorators for Various Application Functionalities
    """
    
    @staticmethod
    def jwt_required(roles=None):
        """
        Decorator to require JWT authentication with optional role-based access
        
        :param roles: List of allowed roles
        :return: Decorated function
        """
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                try:
                    # Verify JWT token
                    verify_jwt_in_request()
                    
                    # Get current user
                    user_id = get_jwt_identity()
                    user = User.query.get(user_id)
                    
                    # Check role-based access if specified
                    if roles and user:
                        if user.role not in roles:
                            return jsonify({
                                'error': 'Insufficient Permissions',
                                'message': 'You do not have access to this resource',
                                'status_code': 403
                            }), 403
                    
                    return fn(*args, **kwargs)
                
                except Exception as e:
                    current_app.logger.error(f"Authentication error: {str(e)}")
                    return jsonify({
                        'error': 'Authentication Failed',
                        'message': str(e),
                        'status_code': 401
                    }), 401
            return wrapper
        return decorator

    @staticmethod
    def rate_limit(limit=100, per=60):
        """
        Rate limiting decorator to prevent abuse
        
        :param limit: Maximum number of requests
        :param per: Time window in seconds
        :return: Decorated function
        """
        def decorator(fn):
            requests = {}
            
            @wraps(fn)
            def wrapper(*args, **kwargs):
                # Get client IP
                client_ip = request.remote_addr
                
                # Get current time
                current_time = time.time()
                
                # Clean up old requests
                requests[client_ip] = [
                    t for t in requests.get(client_ip, []) 
                    if current_time - t < per
                ]
                
                # Check rate limit
                if len(requests.get(client_ip, [])) >= limit:
                    return jsonify({
                        'error': 'Rate Limit Exceeded',
                        'message': f'Too many requests. Limit is {limit} per {per} seconds',
                        'status_code': 429
                    }), 429
                
                # Add current request timestamp
                requests.setdefault(client_ip, []).append(current_time)
                
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def log_execution_time(logger=None):
        """
        Decorator to log function execution time
        
        :param logger: Optional custom logger
        :return: Decorated function
        """
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = fn(*args, **kwargs)
                    
                    # Log execution time
                    execution_time = time.time() - start_time
                    log = logger or current_app.logger
                    log.info(f"{fn.__name__} executed in {execution_time:.4f} seconds")
                    
                    return result
                
                except Exception as e:
                    # Log any exceptions
                    log = logger or current_app.logger
                    log.error(f"Error in {fn.__name__}: {str(e)}")
                    raise
            return wrapper
        return decorator

# Export decorator functions
jwt_required = Decorators.jwt_required
rate_limit = Decorators.rate_limit
log_execution_time = Decorators.log_execution_time