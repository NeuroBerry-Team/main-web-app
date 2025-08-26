import time
from functools import wraps
from flask import current_app, request, g


class SessionManager:
    """Enhanced session management utilities"""
    
    # Store active sessions in memory (in production, use Redis)
    active_sessions = {}
    session_metadata = {}
    
    @classmethod
    def create_session(cls, user_id, token, user_agent=None, ip_address=None):
        """
        Create a new session record
        
        Args:
            user_id: User identifier
            token: JWT token
            user_agent: User agent string
            ip_address: Client IP address
        """
        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'user_agent': user_agent,
            'ip_address': ip_address,
            'is_active': True
        }
        
        cls.active_sessions[token] = session_data
        
        # Keep user metadata separate
        if user_id not in cls.session_metadata:
            cls.session_metadata[user_id] = []
        
        cls.session_metadata[user_id].append({
            'token': token,
            'created_at': session_data['created_at'],
            'user_agent': user_agent,
            'ip_address': ip_address
        })
    
    @classmethod
    def validate_session(cls, token):
        """
        Validate an existing session
        
        Args:
            token: JWT token to validate
            
        Returns:
            dict: Session data if valid, None otherwise
        """
        if token not in cls.active_sessions:
            return None
        
        session = cls.active_sessions[token]
        
        if not session.get('is_active', False):
            return None
        
        # Check session timeout (24 hours)
        if time.time() - session['last_activity'] > 86400:
            cls.invalidate_session(token)
            return None
        
        # Update last activity
        session['last_activity'] = time.time()
        
        return session
    
    @classmethod
    def invalidate_session(cls, token):
        """
        Invalidate a specific session
        
        Args:
            token: JWT token to invalidate
        """
        if token in cls.active_sessions:
            session = cls.active_sessions[token]
            user_id = session.get('user_id')
            
            # Mark as inactive
            session['is_active'] = False
            
            # Remove from active sessions
            del cls.active_sessions[token]
            
            # Clean up user metadata
            if user_id in cls.session_metadata:
                cls.session_metadata[user_id] = [
                    s for s in cls.session_metadata[user_id]
                    if s['token'] != token
                ]
    
    @classmethod
    def invalidate_all_user_sessions(cls, user_id):
        """
        Invalidate all sessions for a specific user
        
        Args:
            user_id: User identifier
        """
        # Get all tokens for this user
        user_tokens = []
        for token, session in cls.active_sessions.items():
            if session.get('user_id') == user_id:
                user_tokens.append(token)
        
        # Invalidate each token
        for token in user_tokens:
            cls.invalidate_session(token)
        
        # Clean up metadata
        if user_id in cls.session_metadata:
            del cls.session_metadata[user_id]
    
    @classmethod
    def get_user_sessions(cls, user_id):
        """
        Get all active sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            list: List of session information
        """
        sessions = []
        for token, session in cls.active_sessions.items():
            if session.get('user_id') == user_id and session.get('is_active'):
                sessions.append({
                    'token_hash': hash(token),  # Don't expose full token
                    'created_at': session['created_at'],
                    'last_activity': session['last_activity'],
                    'user_agent': session.get('user_agent'),
                    'ip_address': session.get('ip_address')
                })
        return sessions
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """
        Clean up expired sessions (should be run periodically)
        """
        current_time = time.time()
        expired_tokens = []
        
        for token, session in cls.active_sessions.items():
            if current_time - session['last_activity'] > 86400:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            cls.invalidate_session(token)
        
        current_app.logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
    
    @classmethod
    def detect_suspicious_activity(cls, token, user_agent=None, ip_address=None):
        """
        Detect potentially suspicious session activity
        
        Args:
            token: JWT token
            user_agent: Current user agent
            ip_address: Current IP address
            
        Returns:
            bool: True if suspicious activity detected
        """
        if token not in cls.active_sessions:
            return True  # Invalid session is suspicious
        
        session = cls.active_sessions[token]
        
        # Check for user agent changes
        if (session.get('user_agent') and user_agent and 
            session['user_agent'] != user_agent):
            current_app.logger.warning(
                f"User agent change detected for user {session['user_id']}"
            )
            return True
        
        # Check for IP address changes (basic check)
        if (session.get('ip_address') and ip_address and 
            session['ip_address'] != ip_address):
            current_app.logger.warning(
                f"IP address change detected for user {session['user_id']}"
            )
            # Note: This might be too strict for mobile users
            # Consider implementing IP range checking instead
        
        return False


def require_valid_session(f):
    """
    Decorator to ensure valid session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return {'error': 'No session token'}, 401
        
        # Validate session
        session = SessionManager.validate_session(token)
        if not session:
            return {'error': 'Invalid or expired session'}, 401
        
        # Check for suspicious activity
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        
        if SessionManager.detect_suspicious_activity(token, user_agent, ip_address):
            SessionManager.invalidate_session(token)
            return {'error': 'Suspicious activity detected'}, 401
        
        # Store session info in g for use in the route
        g.session = session
        g.user_id = session['user_id']
        
        return f(*args, **kwargs)
    
    return decorated_function
