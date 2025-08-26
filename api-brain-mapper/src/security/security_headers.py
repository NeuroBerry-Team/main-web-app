import os


def add_security_headers(response):
    """Add security headers to Flask responses"""
    
    # Content Security Policy - Strict policy
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # In development, we might need to be more permissive
    if os.getenv('ENV_MODE') != 'production':
        csp_policy = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "img-src 'self' data: blob: http://localhost:*"
        )
    
    # Security headers
    response.headers['Content-Security-Policy'] = csp_policy
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), '
        'payment=(), usb=(), magnetometer=(), gyroscope=()'
    )
    
    # HSTS in production
    if os.getenv('ENV_MODE') == 'production':
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains; preload'
        )
    
    # Cache control for sensitive endpoints
    if '/auth/' in str(response.location or ''):
        response.headers['Cache-Control'] = (
            'no-store, no-cache, must-revalidate, proxy-revalidate'
        )
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response


def setup_security_headers(app):
    """Setup security headers for Flask app"""
    
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)
    
    return app
