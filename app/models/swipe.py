# app/models/swipe.py — Swipe action model (track/artist/playlist likes)

from datetime import datetime
from app.extensions import db


class Swipe(db.Model):
    """Swipe action model for explore feature."""
    
    __tablename__ = 'swipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.String(100), nullable=False)  # Spotify track/artist/playlist ID
    content_type = db.Column(db.String(50), nullable=False)  # 'track', 'artist', 'playlist'
    liked = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Serialize swipe to dict for JSON responses
    def to_dict(self):
        """Convert swipe to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'liked': self.liked,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
