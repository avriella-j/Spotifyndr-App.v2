# app/models/spotify_cache.py — Cached Spotify API responses

from datetime import datetime
from app.extensions import db


class SpotifyCache(db.Model):
    """Cache for Spotify API responses."""
    
    __tablename__ = 'spotify_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.JSON)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
