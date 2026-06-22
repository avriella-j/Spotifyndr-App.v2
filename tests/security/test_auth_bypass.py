import pytest
from flask import url_for


def test_protected_route_requires_auth(client):
    """Test protected routes require authentication."""
    response = client.get(url_for('fyp.fyp'))
    assert response.status_code == 302  # Redirect to login


def test_api_requires_auth(client):
    """Test API endpoints require authentication."""
    response = client.get('/api/v1/users')
    # Either 401 or 302 (redirect to login) both indicate auth requirement
    assert response.status_code in [401, 302]
