# app/models/notification.py — Notification model

from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """Notification model."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'follow', 'message', 'recommendation'
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text)
    data = db.Column(db.JSON)  # Additional data
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Serialize notification to dict for JSON responses
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
