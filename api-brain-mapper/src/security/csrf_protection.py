import secrets
import hashlib
import time
from functools import wraps
from flask import request, session, abort, current_app


class CSRFProtection:
    """CSRF protection utilities"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection with Flask app"""
        app.config.setdefault('CSRF_SECRET_KEY', secrets.token_hex(32))
        app.config.setdefault('CSRF_TOKEN_TIMEOUT', 3600)  # 1 hour
        
        # Add before_request handler
        @app.before_request
        def csrf_protect():
            if self._should_check_csrf():
                self._validate_csrf_token()
    
    def _should_check_csrf(self):
        """Determine if CSRF check should be performed"""
        # Skip CSRF check for:
        # - GET, HEAD, OPTIONS requests (safe methods)
        # - Certain endpoints that don't need CSRF protection
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return False
        
        # Skip for authentication endpoints using other protection
        exempt_endpoints = [
            'auth.login',
            'auth.logout',
            'auth.isLoggedIn'
        ]
        
        if request.endpoint in exempt_endpoints:
            return False
        
        return True
    
    def _validate_csrf_token(self):
        """Validate CSRF token from request"""
        token = self._get_csrf_token_from_request()
        
        if not token:
            current_app.logger.warning(
                f"CSRF token missing for {request.method} {request.path}"
            )
            abort(403, 'CSRF token missing')
        
        if current_app.config.get('DEBUG'):
            current_app.logger.debug(f"[CSRF DEBUG] Validating token: {token[:20]}...")
        
        if not self._is_valid_csrf_token(token):
            current_app.logger.warning(
                f"Invalid CSRF token for {request.method} {request.path}"
            )
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Token validation failed for: {token}")
            abort(403, 'Invalid CSRF token')
    
    def _get_csrf_token_from_request(self):
        """Extract CSRF token from request headers or form data"""
        # Try header first
        token = request.headers.get('X-CSRF-Token')
        
        # Try form data if header not present
        if not token and request.form:
            token = request.form.get('csrf_token')
        
        # Try JSON data
        if not token and request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                token = json_data.get('csrf_token')
        
        return token
    
    def _is_valid_csrf_token(self, token):
        """Validate CSRF token"""
        try:
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Parsing token: {token[:20]}...")
            
            # Decode token parts
            parts = token.split('.')
            if len(parts) != 3:
                if current_app.config.get('DEBUG'):
                    current_app.logger.debug("[CSRF DEBUG] Token has wrong number of parts")
                return False
            
            timestamp_str, session_id, signature = parts
            timestamp = int(timestamp_str)  # Use int instead of float
            
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Token timestamp: {timestamp}")
                current_app.logger.debug(f"[CSRF DEBUG] Current time: {int(time.time())}")
            
            # Check if token is expired
            timeout = current_app.config.get('CSRF_TOKEN_TIMEOUT', 3600)
            time_diff = int(time.time()) - timestamp
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Time difference: {time_diff}s (timeout: {timeout}s)")
            
            if time_diff > timeout:
                if current_app.config.get('DEBUG'):
                    current_app.logger.debug("[CSRF DEBUG] Token expired")
                return False
            
            # Verify signature
            expected_signature = self._generate_csrf_signature(
                timestamp_str, session_id
            )
            
            signature_match = secrets.compare_digest(signature, expected_signature)
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Signature match: {signature_match}")
            
            return signature_match
            
        except (ValueError, TypeError, OverflowError) as e:
            if current_app.config.get('DEBUG'):
                current_app.logger.debug(f"[CSRF DEBUG] Token parsing error: {e}")
            return False
    
    def _generate_csrf_signature(self, timestamp_str, session_id):
        """Generate CSRF token signature"""
        secret_key = current_app.config['CSRF_SECRET_KEY']
        
        # Create signature using HMAC
        data = f"{timestamp_str}.{session_id}".encode('utf-8')
        signature = hashlib.pbkdf2_hmac(
            'sha256',
            data,
            secret_key.encode('utf-8'),
            100000  # iterations
        )
        
        return signature.hex()
    
    def generate_csrf_token(self, session_id=None):
        """Generate new CSRF token"""
        if not session_id:
            # Use session ID or generate one
            session_id = session.get('_csrf_session_id')
            if not session_id:
                session_id = secrets.token_hex(16)
                session['_csrf_session_id'] = session_id
        
        # Use integer timestamp to avoid decimal points in token
        timestamp_str = str(int(time.time()))
        signature = self._generate_csrf_signature(timestamp_str, session_id)
        
        token = f"{timestamp_str}.{session_id}.{signature}"
        if current_app.config.get('DEBUG'):
            current_app.logger.debug(f"[CSRF DEBUG] Generated token: {token[:20]}...")
            current_app.logger.debug(f"[CSRF DEBUG] Token timestamp: {timestamp_str}")
        return token


# Global CSRF protection instance
csrf = CSRFProtection()


def csrf_exempt(f):
    """Decorator to exempt a route from CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mark request as CSRF exempt
        request._csrf_exempt = True
        return f(*args, **kwargs)
    return decorated_function


def require_csrf_token(f):
    """Decorator to explicitly require CSRF token validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, '_csrf_exempt'):
            csrf._validate_csrf_token()
        return f(*args, **kwargs)
    return decorated_function


def get_csrf_token():
    """Helper function to get CSRF token for templates/frontend"""
    return csrf.generate_csrf_token()
