from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.dbConnection import db


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    loginAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    logoutAt = Column(DateTime, nullable=True)
    ipAddress = Column(String(45), nullable=True)
    userAgent = Column(String(200), nullable=True)
    
    # Relationship to User model
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f'<UserSession {self.userId} - {self.loginAt}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'loginAt': (self.loginAt.isoformat() + 'Z'
                        if self.loginAt else None),
            'logoutAt': (self.logoutAt.isoformat() + 'Z'
                         if self.logoutAt else None),
            'ipAddress': self.ipAddress,
            'userAgent': self.userAgent,
            'isActive': self.logoutAt is None
        }
    
    @classmethod
    def create_session(cls, user_id, ip_address=None, user_agent=None):
        """Create a new login session"""
        truncated_agent = user_agent[:200] if user_agent else None
        session = cls(
            userId=user_id,
            loginAt=datetime.utcnow(),
            ipAddress=ip_address,
            userAgent=truncated_agent
        )
        return session
    
    def close_session(self):
        """Close this session"""
        if not self.logoutAt:
            self.logoutAt = datetime.utcnow()
    
    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        if not self.logoutAt:
            return None
        return int((self.logoutAt - self.loginAt).total_seconds() / 60)
    
    @property
    def is_active(self):
        """Check if session is still active"""
        return self.logoutAt is None
    
    @classmethod
    def get_active_sessions(cls, user_id):
        """Get all active sessions for a user"""
        return cls.query.filter_by(userId=user_id, logoutAt=None).all()
    
    @classmethod
    def close_all_sessions(cls, user_id):
        """Close all active sessions for a user"""
        active_sessions = cls.get_active_sessions(user_id)
        for session in active_sessions:
            session.close_session()
        return len(active_sessions)
    
    @classmethod
    def get_recent_sessions(cls, user_id, days=30):
        """Get recent sessions for a user within specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(
            cls.userId == user_id,
            cls.loginAt >= cutoff_date
        ).order_by(cls.loginAt.desc()).all()
