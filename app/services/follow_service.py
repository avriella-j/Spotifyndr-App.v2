# app/services/follow_service.py — Follow/unfollow logic

from app.models.follow import Follow
from app.models.block import Block
from app.models.user import User
from app.extensions import db


class FollowService:
    """Follow/unfollow logic."""
    
    @staticmethod
    # Follow a user (with block check)
    def follow_user(follower_id, followed_id):
        """Follow a user."""
        # Check if already following
        existing = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first()
        
        if existing:
            return
        
        # Check if blocked
        block = Block.query.filter_by(
            blocker_id=followed_id,
            blocked_id=follower_id
        ).first()
        
        if block:
            raise ValueError("Cannot follow user who has blocked you")
        
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.session.add(follow)
        db.session.commit()
    
    @staticmethod
    # Remove a follow relationship
    def unfollow_user(follower_id, followed_id):
        """Unfollow a user."""
        follow = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first()
        
        if follow:
            db.session.delete(follow)
            db.session.commit()
    
    @staticmethod
    def get_followers(user_id):
        """Get user's followers."""
        return Follow.query.filter_by(followed_id=user_id).all()
    
    @staticmethod
    def get_following(user_id):
        """Get users that user is following."""
        return Follow.query.filter_by(follower_id=user_id).all()
    
    @staticmethod
    def is_following(follower_id, followed_id):
        """Check if user is following another user."""
        return Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first() is not None
