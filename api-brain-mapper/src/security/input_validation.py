import re
from flask import abort
from email_validator import validate_email, EmailNotValidError


class InputValidator:
    """Input validation and sanitization utilities"""
    
    @staticmethod
    def validate_email_format(email):
        """Validate email format and return normalized email"""
        if not email or not isinstance(email, str):
            abort(400, 'Invalid email format')
        
        try:
            # Validate and normalize email
            valid_email = validate_email(email)
            return valid_email.email
        except EmailNotValidError:
            abort(400, 'Invalid email format')
    
    @staticmethod
    def validate_password(password, min_length=8, max_length=128):
        """Validate password strength"""
        if not password or not isinstance(password, str):
            abort(400, 'Password is required')
        
        if len(password) < min_length:
            abort(400, f'Password must be at least {min_length} characters')
        
        if len(password) > max_length:
            abort(400, f'Password must not exceed {max_length} characters')
        
        # Check for basic complexity
        if not re.search(r'[A-Za-z]', password):
            abort(400, 'Password must contain at least one letter')
        
        if not re.search(r'\d', password):
            abort(400, 'Password must contain at least one number')
        
        return password
    
    @staticmethod
    def validate_name(name, field_name="Name", min_length=1, max_length=100):
        """Validate name fields"""
        if not name or not isinstance(name, str):
            abort(400, f'{field_name} is required')
        
        # Strip whitespace and check length
        name = name.strip()
        if len(name) < min_length:
            abort(400, f'{field_name} is too short')
        
        if len(name) > max_length:
            abort(400, f'{field_name} is too long')
        
        # Only allow letters, spaces, hyphens, and apostrophes
        if not re.match(r'^[A-Za-zÀ-ÿ\s\-\']+$', name):
            abort(400, f'{field_name} contains invalid characters')
        
        return name
    
    @staticmethod
    def validate_json_request(request, required_fields):
        """Validate JSON request has required fields"""
        if not request.is_json:
            abort(400, 'Request must be JSON')
        
        try:
            data = request.get_json()
        except Exception:
            abort(400, 'Invalid JSON format')
        
        if not data:
            abort(400, 'Request body is required')
        
        missing_fields = [field for field in required_fields
                          if field not in data]
        if missing_fields:
            fields_list = ", ".join(missing_fields)
            abort(400, f'Missing required fields: {fields_list}')
        
        return data
    
    @staticmethod
    def sanitize_string(value, max_length=500):
        """Basic string sanitization"""
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        
        # Strip whitespace and limit length
        sanitized = value.strip()[:max_length]
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def validate_integer(value, field_name="Value", min_value=None,
                         max_value=None):
        """Validate integer values"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                abort(400, f'{field_name} must be an integer')
        
        if min_value is not None and value < min_value:
            abort(400, f'{field_name} must be at least {min_value}')
        
        if max_value is not None and value > max_value:
            abort(400, f'{field_name} must not exceed {max_value}')
        
        return value
