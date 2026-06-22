# app/tasks/token_refresh.py — Celery tasks for Spotify token refresh

from app.tasks.celery_app import celery
from app.models.user import User
from app.auth.spotify_oauth import SpotifyOAuth
from app.services.token_service import TokenService
from app.extensions import db
from datetime import datetime


@celery.task
# Refresh a single user's Spotify access token
def refresh_user_token(user_id):
    """Refresh Spotify access token for a user."""
    user = User.query.get(user_id)
    if not user:
        return
    
    refresh_token = TokenService.decrypt_token(user.refresh_token)
    spotify_oauth = SpotifyOAuth()
    
    try:
        token_data = spotify_oauth.refresh_access_token(refresh_token)
        
        user.access_token = TokenService.encrypt_token(token_data['access_token'])
        user.refresh_token = TokenService.encrypt_token(token_data.get('refresh_token', refresh_token))
        user.token_expires_at = datetime.fromtimestamp(token_data['expires_at'])
        
        db.session.commit()
        
        return {'status': 'success', 'user_id': user_id}
    except Exception as e:
        return {'status': 'error', 'user_id': user_id, 'error': str(e)}


@celery.task
# Find and refresh all tokens expiring within the next hour
def refresh_expiring_tokens():
    """Refresh all tokens that are expiring soon."""
    from datetime import timedelta
    
    # Find tokens expiring in the next hour
    expiry_threshold = datetime.utcnow() + timedelta(hours=1)
    
    users = User.query.filter(
        User.token_expires_at < expiry_threshold
    ).all()
    
    for user in users:
        refresh_user_token.delay(user.id)
    
    return {'status': 'success', 'count': len(users)}
