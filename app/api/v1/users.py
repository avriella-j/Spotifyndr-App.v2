from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.services.spotify_sync_service import SpotifySyncService
from app.models.user_top_content import UserTopContent


@login_required
def get_users():
    """Get list of users with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = UserService.get_users_paginated(page, per_page)
    return jsonify([user.to_dict() for user in users.items])


@login_required
def get_user(user_id):
    """Get user by ID."""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@login_required
def update_user(user_id):
    """Update user profile."""
    if user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    user = UserService.update_user(user_id, data)
    return jsonify(user.to_dict())


@login_required
def delete_user(user_id):
    """Delete user account."""
    if user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    UserService.delete_user(user_id)
    return jsonify({'message': 'User deleted successfully'})


@login_required
def get_my_top_tracks():
    """Get current user's top tracks (synced from Spotify)."""
    try:
        content = SpotifySyncService.sync_if_stale(current_user)
        tracks = content.top_tracks if content and content.top_tracks else []
        return jsonify(tracks)
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 500


@login_required
def get_my_top_artists():
    """Get current user's top artists (synced from Spotify)."""
    try:
        content = SpotifySyncService.sync_if_stale(current_user)
        artists = content.top_artists if content and content.top_artists else []
        return jsonify(artists)
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 500


@login_required
def search_users():
    """Search users by display name."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    users = UserService.search_users(q)
    return jsonify([u.to_dict() for u in users])


@login_required
def update_my_profile():
    """Update current user's profile (bio, image_url, display_name)."""
    data = request.get_json()
    
    if 'display_name' in data:
        current_user.display_name = data['display_name']
    if 'image_url' in data:
        current_user.image_url = data['image_url']
    if 'bio' in data:
        current_user.bio = data['bio']
    
    from app.extensions import db
    db.session.commit()
    
    return jsonify(current_user.to_dict())


@login_required
def delete_my_account():
    """Delete current user's account."""
    UserService.delete_user(current_user.id)
    return jsonify({'message': 'User deleted successfully'})


@login_required
def user_top_tracks(user_id):
    """Get another user's top tracks from DB."""
    content = UserTopContent.query.filter_by(user_id=user_id).first()
    tracks = content.top_tracks if content and content.top_tracks else []
    return jsonify(tracks)


@login_required
def user_top_artists(user_id):
    """Get another user's top artists from DB."""
    content = UserTopContent.query.filter_by(user_id=user_id).first()
    artists = content.top_artists if content and content.top_artists else []
    return jsonify(artists)
