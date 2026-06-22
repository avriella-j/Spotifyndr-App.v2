import pytest
from flask import url_for


def test_get_conversations(client, app):
    """Test getting user conversations."""
    with app.app_context():
        from app.models.user import User
        from app.extensions import db
        
        # Create test user
        user = User(spotify_id='test', display_name='Test')
        db.session.add(user)
        db.session.commit()
        
        # Login
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
        
        response = client.get(url_for('api.get_conversations'))
        assert response.status_code == 200


def test_create_conversation(client, app):
    """Test creating a conversation."""
    with app.app_context():
        from app.models.user import User
        from app.extensions import db
        
        # Create test users
        user1 = User(spotify_id='user1', display_name='User 1')
        user2 = User(spotify_id='user2', display_name='User 2')
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Login as user1
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
        
        response = client.post(url_for('api.create_conversation'), json={
            'participant_id': user2.id
        })
        assert response.status_code == 200
