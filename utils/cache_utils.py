from functools import wraps
from flask import current_app
from extensions import cache
import hashlib
import json
import logging

class CacheManager:
    """
    Advanced Caching Utility Class
    """
    
    @staticmethod
    def generate_cache_key(*args, **kwargs):
        """
        Generate a unique cache key based on input arguments
        
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: Unique cache key
        """
        # Convert arguments to a hashable string
        key_parts = []
        
        # Add positional arguments
        key_parts.extend(str(arg) for arg in args)
        
        # Add sorted keyword arguments
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        # Create a hash of the combined string
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    @staticmethod
    def cached_service(timeout=300, key_prefix='service_'):
        """
        Decorator for caching service method results
        
        :param timeout: Cache timeout in seconds
        :param key_prefix: Prefix for cache key
        :return: Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate unique cache key
                cache_key = f"{key_prefix}{func.__name__}:{CacheManager.generate_cache_key(*args, **kwargs)}"
                
                try:
                    # Try to get cached result
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        current_app.logger.info(f"Cache hit for {cache_key}")
                        return cached_result
                    
                    # Call original function
                    result = func(*args, **kwargs)
                    
                    # Cache the result
                    cache.set(cache_key, result, timeout=timeout)
                    current_app.logger.info(f"Cached result for {cache_key}")
                    
                    return result
                
                except Exception as e:
                    current_app.logger.error(f"Caching error: {e}")
                    # Fallback to original function if caching fails
                    return func(*args, **kwargs)
            
            # Add method to clear this specific cache
            def clear_cache(*args, **kwargs):
                cache_key = f"{key_prefix}{func.__name__}:{CacheManager.generate_cache_key(*args, **kwargs)}"
                cache.delete(cache_key)
                current_app.logger.info(f"Cleared cache for {cache_key}")
            
            wrapper.clear_cache = clear_cache
            return wrapper
        return decorator

    @staticmethod
    def clear_all_caches():
        """
        Clear all caches
        """
        try:
            cache.clear()
            current_app.logger.info("All caches cleared successfully")
        except Exception as e:
            current_app.logger.error(f"Error clearing caches: {e}")

# Expose commonly used methods
cached_service = CacheManager.cached_service
clear_all_caches = CacheManager.clear_all_caches