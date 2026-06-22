# app/models/user_top_content.py — User's top Spotify tracks/artists

from datetime import datetime
from app.extensions import db


class UserTopContent(db.Model):
    """User's top tracks and artists from Spotify."""
    
    __tablename__ = 'user_top_content'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    top_tracks = db.Column(db.JSON)
    top_artists = db.Column(db.JSON)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
