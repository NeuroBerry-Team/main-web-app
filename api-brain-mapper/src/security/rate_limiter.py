import time
import os
from functools import wraps
from flask import request, abort
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self):
        # Store login attempts per IP
        self.login_attempts = defaultdict(deque)
        # Store account lockout timestamps
        self.locked_accounts = {}
    
    def is_rate_limited(self, ip_address, max_attempts=5, window_minutes=15):
        """Check if IP is rate limited for login attempts"""
        now = time.time()
        window_seconds = window_minutes * 60
        
        # Clean old attempts
        while (self.login_attempts[ip_address] and
               now - self.login_attempts[ip_address][0] > window_seconds):
            self.login_attempts[ip_address].popleft()
        
        # Check if exceeded attempts
        if len(self.login_attempts[ip_address]) >= max_attempts:
            return True
        
        return False
    
    def record_attempt(self, ip_address):
        """Record a login attempt"""
        self.login_attempts[ip_address].append(time.time())
    
    def is_account_locked(self, email, lockout_minutes=30):
        """Check if account is locked due to multiple failed attempts"""
        if email not in self.locked_accounts:
            return False
        
        lock_time = self.locked_accounts[email]
        if time.time() - lock_time > (lockout_minutes * 60):
            # Unlock account
            del self.locked_accounts[email]
            return False
        
        return True
    
    def lock_account(self, email):
        """Lock account after too many failed attempts"""
        self.locked_accounts[email] = time.time()


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_login(max_attempts=5, window_minutes=15):
    """Decorator for rate limiting login attempts"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip rate limiting in development mode
            if os.getenv('ENV_MODE') != 'production':
                return f(*args, **kwargs)
            
            ip_address = request.remote_addr
            
            if rate_limiter.is_rate_limited(ip_address, max_attempts,
                                            window_minutes):
                abort(429, 'Too many login attempts. Please try again later.')
            
            # Record this attempt
            rate_limiter.record_attempt(ip_address)
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def rate_limit_api(max_attempts=100, window_minutes=60):
    """General API rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip rate limiting in development mode
            if os.getenv('ENV_MODE') != 'production':
                return f(*args, **kwargs)
            
            ip_address = request.remote_addr
            
            if rate_limiter.is_rate_limited(ip_address, max_attempts,
                                            window_minutes):
                abort(429, 'Too many requests. Please try again later.')
            
            # Record this attempt
            rate_limiter.record_attempt(ip_address)
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def rate_limit_file_upload(max_attempts=20, window_minutes=60):
    """Rate limiting for file upload endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip rate limiting in development mode
            if os.getenv('ENV_MODE') != 'production':
                return f(*args, **kwargs)
            
            ip_address = request.remote_addr
            
            if rate_limiter.is_rate_limited(ip_address, max_attempts,
                                            window_minutes):
                abort(429, 'Too many upload requests. Please try again later.')
            
            # Record this attempt
            rate_limiter.record_attempt(ip_address)
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def check_account_lockout(email):
    """Check if account is locked and abort if it is"""
    if rate_limiter.is_account_locked(email):
        abort(423, 'Account temporarily locked due to multiple failed '
                   'login attempts')


def handle_failed_login(email, max_failures=3):
    """Handle failed login attempt - potentially lock account"""
    if os.getenv('ENV_MODE') == 'production':
        # For now, we'll use the in-memory solution
        rate_limiter.lock_account(email)
