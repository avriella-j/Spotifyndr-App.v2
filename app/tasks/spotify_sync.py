# app/tasks/spotify_sync.py — Celery tasks for Spotify data import

from app.tasks.celery_app import celery
from app.models.user import User
from app.services.spotify_service import SpotifyService
from app.services.token_service import TokenService
from app.models.user_top_content import UserTopContent
from app.extensions import db
from datetime import datetime


@celery.task
# Full import of top tracks/artists from Spotify
def full_spotify_import(user_id):
    """Import all Spotify data for a user."""
    user = User.query.get(user_id)
    if not user:
        return
    
    access_token = TokenService.decrypt_token(user.access_token)
    spotify = SpotifyService(access_token)
    
    # Get top tracks and artists
    top_tracks = spotify.get_top_tracks(limit=50)
    top_artists = spotify.get_top_artists(limit=50)
    
    # Store in database
    top_content = UserTopContent.query.filter_by(user_id=user_id).first()
    if not top_content:
        top_content = UserTopContent(user_id=user_id)
        db.session.add(top_content)
    
    top_content.top_tracks = top_tracks
    top_content.top_artists = top_artists
    top_content.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return {'status': 'success', 'user_id': user_id}


@celery.task
# Incremental sync of recent Spotify top content
def sync_user_spotify(user_id):
    """Sync user's Spotify data (incremental update)."""
    user = User.query.get(user_id)
    if not user:
        return
    
    # Check if token needs refresh
    if TokenService.is_token_expired(user.token_expires_at):
        # Trigger token refresh task
        refresh_user_token.delay(user_id)
        return
    
    access_token = TokenService.decrypt_token(user.access_token)
    spotify = SpotifyService(access_token)
    
    # Get recent top tracks and artists
    top_tracks = spotify.get_top_tracks(limit=20, time_range='short_term')
    top_artists = spotify.get_top_artists(limit=20, time_range='short_term')
    
    # Update database
    top_content = UserTopContent.query.filter_by(user_id=user_id).first()
    if top_content:
        top_content.top_tracks = top_tracks
        top_content.top_artists = top_artists
        top_content.updated_at = datetime.utcnow()
        db.session.commit()
    
    return {'status': 'success', 'user_id': user_id}
