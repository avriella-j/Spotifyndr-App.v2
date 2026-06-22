# app/models/block.py — Block relationship model

from datetime import datetime
from app.extensions import db


class Block(db.Model):
    """Block relationship model."""
    
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),)
