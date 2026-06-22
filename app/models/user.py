# app/models/user.py — User model (Spotify OAuth, profile, relationships)

from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """User model for Spotifyndr users."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    image_url = db.Column(db.String(500))
    bio = db.Column(db.Text, default='')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Encrypted Spotify token storage
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    
    # ORM relationships to other models
    follows = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followed_by = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    conversations = db.relationship('Conversation', secondary='conversation_participants', backref='participants')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    swipes = db.relationship('Swipe', backref='user', lazy='dynamic')
    feature_vector = db.relationship('UserFeatureVector', backref='user', uselist=False)
    top_content = db.relationship('UserTopContent', backref='user', uselist=False)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    blocks = db.relationship('Block', foreign_keys='Block.blocker_id', backref='blocker', lazy='dynamic')
    blocked_by = db.relationship('Block', foreign_keys='Block.blocked_id', backref='blocked', lazy='dynamic')
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'spotify_id': self.spotify_id,
            'display_name': self.display_name,
            'email': self.email,
            'image_url': self.image_url,
            'bio': self.bio or '',
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
