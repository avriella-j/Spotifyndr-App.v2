# app/tasks/maintenance.py — Periodic cleanup tasks (cache, old data)

from app.tasks.celery_app import celery
from app.models.spotify_cache import SpotifyCache
from app.models.notification import Notification
from app.extensions import db
from datetime import datetime, timedelta


@celery.task
# Remove expired Spotify cache entries from DB
def cleanup_expired_cache():
    """Clean up expired Spotify cache entries."""
    now = datetime.utcnow()
    
    expired_entries = SpotifyCache.query.filter(
        SpotifyCache.expires_at < now
    ).all()
    
    for entry in expired_entries:
        db.session.delete(entry)
    
    db.session.commit()
    
    return {'status': 'success', 'deleted': len(expired_entries)}


@celery.task
# Permanently delete old read notifications (30+ days)
def process_deletions():
    """Process soft-deleted records for permanent deletion."""
    # Delete notifications older than 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    old_notifications = Notification.query.filter(
        Notification.created_at < thirty_days_ago,
        Notification.read == True
    ).all()
    
    for notification in old_notifications:
        db.session.delete(notification)
    
    db.session.commit()
    
    return {'status': 'success', 'deleted': len(old_notifications)}
