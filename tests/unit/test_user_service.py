import pytest
from app.services.user_service import UserService
from app.models.user import User
from app.extensions import db


def test_get_user_by_id(app):
    """Test getting user by ID."""
    with app.app_context():
        user = User(
            spotify_id='test123',
            display_name='Test User',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved = UserService.get_user_by_id(user.id)
        assert retrieved is not None
        assert retrieved.spotify_id == 'test123'


def test_get_or_create_user(app):
    """Test getting or creating user."""
    with app.app_context():
        user = UserService.get_or_create_user(
            spotify_id='test123',
            display_name='Test User',
            email='test@example.com',
            images=[],
            access_token='token',
            refresh_token='refresh',
            expires_at=None
        )
        
        assert user is not None
        assert user.spotify_id == 'test123'
        
        # Test getting existing user
        user2 = UserService.get_or_create_user(
            spotify_id='test123',
            display_name='Test User',
            email='test@example.com',
            images=[],
            access_token='token',
            refresh_token='refresh',
            expires_at=None
        )
        
        assert user.id == user2.id
