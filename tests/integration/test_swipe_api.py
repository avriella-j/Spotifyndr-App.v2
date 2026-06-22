import pytest
from flask import url_for


def test_submit_swipe(client, app):
    """Test submitting a swipe."""
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
        
        response = client.post(url_for('api.submit_swipe'), json={
            'content_id': 'track123',
            'liked': True
        })
        assert response.status_code == 200
