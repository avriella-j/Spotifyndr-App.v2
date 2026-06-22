# app/models/recommendation_event.py — Recommendation tracking model

from datetime import datetime
from app.extensions import db


class RecommendationEvent(db.Model):
    """Recommendation event model for tracking recommendations."""
    
    __tablename__ = 'recommendation_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.String(100), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float)
    feedback = db.Column(db.Boolean)  # True if liked, False if disliked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Serialize rec event to dict for JSON responses
    def to_dict(self):
        """Convert recommendation event to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'score': self.score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
