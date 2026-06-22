# app/models/user_similarity.py — User similarity scores model

from datetime import datetime
from app.extensions import db


class UserSimilarity(db.Model):
    """User similarity scores for mutuals feature."""
    
    __tablename__ = 'user_similarities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id_1 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id_2 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id_1', 'user_id_2', name='unique_similarity'),)
