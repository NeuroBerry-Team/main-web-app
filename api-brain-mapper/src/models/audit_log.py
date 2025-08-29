from ..database.dbConnection import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entityType = db.Column(db.String(50), nullable=False)
    entityId = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime(), nullable=False)
