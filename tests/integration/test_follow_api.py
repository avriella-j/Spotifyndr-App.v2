import pytest
from flask import url_for


def test_follow_user(client, app):
    """Test following a user."""
    with app.app_context():
        from app.models.user import User
        from app.extensions import db
        from flask_login import login_user
        
        # Create test users
        user1 = User(spotify_id='user1', display_name='User 1')
        user2 = User(spotify_id='user2', display_name='User 2')
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Login as user1
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
        
        response = client.post(url_for('api.follow_user', user_id=user2.id))
        assert response.status_code == 200


def test_unfollow_user(client, app):
    """Test unfollowing a user."""
    with app.app_context():
        from app.models.user import User
        from app.models.follow import Follow
        from app.extensions import db
        
        # Create test users and follow relationship
        user1 = User(spotify_id='user1', display_name='User 1')
        user2 = User(spotify_id='user2', display_name='User 2')
        db.session.add_all([user1, user2])
        db.session.commit()
        
        follow = Follow(follower_id=user1.id, followed_id=user2.id)
        db.session.add(follow)
        db.session.commit()
        
        # Login as user1
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
        
        response = client.delete(url_for('api.unfollow_user', user_id=user2.id))
        assert response.status_code == 200
