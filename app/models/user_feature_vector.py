# app/models/user_feature_vector.py — ML feature vectors storage

from datetime import datetime
from app.extensions import db


class UserFeatureVector(db.Model):
    """User feature vector for ML recommendations."""
    
    __tablename__ = 'user_feature_vectors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    features = db.Column(db.JSON)  # Serialized feature vector
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
