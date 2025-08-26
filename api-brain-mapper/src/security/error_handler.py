import traceback
from flask import jsonify, current_app, request


class SecureErrorHandler:
    """Secure error handling to prevent information disclosure"""
    
    # Generic error messages for different error types
    GENERIC_MESSAGES = {
        400: "Bad request. Please check your input.",
        401: "Authentication required.",
        403: "Access denied.",
        404: "Resource not found.",
        405: "Method not allowed.",
        409: "Conflict occurred.",
        422: "Invalid input data.",
        429: "Too many requests. Please try again later.",
        500: "An internal error occurred. Please try again later.",
        502: "Service temporarily unavailable.",
        503: "Service unavailable."
    }
    
    @staticmethod
    def handle_error(error):
        """
        Handle errors securely without exposing sensitive information
        
        Args:
            error: The error object
            
        Returns:
            JSON response with generic error message
        """
        # Determine error code
        if hasattr(error, 'code'):
            status_code = error.code
        else:
            status_code = 500
        
        # Log detailed error for debugging (server-side only)
        SecureErrorHandler._log_error(error, status_code)
        
        # Return generic message to client
        message = SecureErrorHandler.GENERIC_MESSAGES.get(
            status_code,
            "An error occurred."
        )
        
        response_data = {
            "error": True,
            "message": message,
            "status_code": status_code
        }
        
        # Add request ID for tracking (if available)
        request_id = getattr(request, 'id', None)
        if request_id:
            response_data['request_id'] = request_id
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def handle_validation_error(field_errors):
        """
        Handle validation errors with sanitized field information
        
        Args:
            field_errors: Dictionary of field validation errors
            
        Returns:
            JSON response with sanitized validation errors
        """
        sanitized_errors = {}
        
        for field, errors in field_errors.items():
            # Only include safe field names
            safe_field = SecureErrorHandler._sanitize_field_name(field)
            
            # Sanitize error messages
            safe_errors = [
                SecureErrorHandler._sanitize_error_message(error)
                for error in errors
            ]
            
            sanitized_errors[safe_field] = safe_errors
        
        response_data = {
            "error": True,
            "message": "Validation failed",
            "errors": sanitized_errors,
            "status_code": 422
        }
        
        return jsonify(response_data), 422
    
    @staticmethod
    def handle_database_error(error):
        """
        Handle database errors without exposing database structure
        
        Args:
            error: Database error object
            
        Returns:
            JSON response with generic database error message
        """
        # Log the actual database error
        current_app.logger.error(
            f"Database error: {str(error)}", 
            extra={'error_type': 'database'}
        )
        
        # Return generic message
        response_data = {
            "error": True,
            "message": "A database error occurred. Please try again.",
            "status_code": 500
        }
        
        return jsonify(response_data), 500
    
    @staticmethod
    def _log_error(error, status_code):
        """
        Log error details for server-side debugging
        
        Args:
            error: Error object
            status_code: HTTP status code
        """
        error_details = {
            'status_code': status_code,
            'error_message': str(error),
            'error_type': type(error).__name__,
            'request_method': request.method if request else None,
            'request_url': request.url if request else None,
            'request_remote_addr': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # Add traceback for 500 errors
        if status_code == 500:
            error_details['traceback'] = traceback.format_exc()
        
        # Log with appropriate level
        if status_code >= 500:
            current_app.logger.error("Server error occurred", extra=error_details)
        elif status_code >= 400:
            current_app.logger.warning("Client error occurred", extra=error_details)
        else:
            current_app.logger.info("Error handled", extra=error_details)
    
    @staticmethod
    def _sanitize_field_name(field_name):
        """
        Sanitize field names to prevent information disclosure
        
        Args:
            field_name: Original field name
            
        Returns:
            Sanitized field name
        """
        # Allow only alphanumeric characters and underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', str(field_name))
        
        # Limit length
        return sanitized[:50]
    
    @staticmethod
    def _sanitize_error_message(error_message):
        """
        Sanitize error messages to remove sensitive information
        
        Args:
            error_message: Original error message
            
        Returns:
            Sanitized error message
        """
        message = str(error_message)
        
        # Remove potentially sensitive patterns
        sensitive_patterns = [
            r'password\s*=\s*[\'"][^\'"]*[\'"]',
            r'token\s*=\s*[\'"][^\'"]*[\'"]',
            r'key\s*=\s*[\'"][^\'"]*[\'"]',
            r'secret\s*=\s*[\'"][^\'"]*[\'"]',
            r'Table\s+[\'"][^\'"]*[\'"]',
            r'Column\s+[\'"][^\'"]*[\'"]',
            r'/[a-zA-Z0-9_/]*\.py',  # File paths
        ]
        
        import re
        for pattern in sensitive_patterns:
            message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
        
        # Limit message length
        return message[:200]
    
    @staticmethod
    def create_error_handlers(app):
        """
        Register secure error handlers with Flask app
        
        Args:
            app: Flask application instance
        """
        
        @app.errorhandler(400)
        def bad_request(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(401)
        def unauthorized(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(403)
        def forbidden(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(404)
        def not_found(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(405)
        def method_not_allowed(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(409)
        def conflict(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(422)
        def unprocessable_entity(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(429)
        def too_many_requests(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(500)
        def internal_error(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(502)
        def bad_gateway(error):
            return SecureErrorHandler.handle_error(error)
        
        @app.errorhandler(503)
        def service_unavailable(error):
            return SecureErrorHandler.handle_error(error)
        
        # Handle general exceptions
        @app.errorhandler(Exception)
        def handle_exception(error):
            # Don't handle HTTP exceptions twice
            if hasattr(error, 'code'):
                return SecureErrorHandler.handle_error(error)
            
            # Handle unexpected exceptions as 500 errors
            current_app.logger.exception("Unexpected error occurred")
            return SecureErrorHandler.handle_error(type('InternalError', (), {'code': 500})())


def setup_secure_error_handling(app):
    """
    Convenience function to set up secure error handling
    
    Args:
        app: Flask application instance
    """
    SecureErrorHandler.create_error_handlers(app)
    
    # Disable debug mode in production
    if not app.debug:
        app.config['PROPAGATE_EXCEPTIONS'] = False
    
    app.logger.info("Secure error handling configured")
