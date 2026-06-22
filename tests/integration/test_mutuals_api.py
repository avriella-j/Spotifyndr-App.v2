import pytest
from flask import url_for


def test_find_mutuals(client, app):
    """Test finding mutual users."""
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
        
        response = client.get(url_for('api.find_mutuals'))
        assert response.status_code == 200
