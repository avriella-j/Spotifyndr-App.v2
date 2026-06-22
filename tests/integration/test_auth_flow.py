import pytest
from flask import url_for


def test_login_redirect(client):
    """Test login redirects to Spotify."""
    response = client.get(url_for('auth.login'))
    assert response.status_code == 302


def test_callback_requires_code(client):
    """Test callback requires authorization code."""
    response = client.get(url_for('auth.callback'))
    assert response.status_code == 302


def test_logout(client):
    """Test logout."""
    response = client.get(url_for('auth.logout'))
    assert response.status_code == 302
