from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.services.spotify_service import SpotifyService
from app.services.token_service import TokenService


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
    """Fetch current user's top tracks from Spotify."""
    limit = request.args.get('limit', 20, type=int)
    time_range = request.args.get('time_range', 'medium_term')
    
    token = TokenService.decrypt_token(current_user.access_token)
    service = SpotifyService(token)
    
    try:
        data = service.get_top_tracks(limit=limit, time_range=time_range)
        items = data.get('items', [])
        result = []
        for item in items:
            album_images = item.get('album', {}).get('images', [])
            result.append({
                'id': item['id'],
                'name': item['name'],
                'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                'image_url': album_images[0]['url'] if album_images else '',
                'album': item.get('album', {}).get('name', ''),
                'popularity': item.get('popularity', 0)
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 500


@login_required
def get_my_top_artists():
    """Fetch current user's top artists from Spotify."""
    limit = request.args.get('limit', 20, type=int)
    time_range = request.args.get('time_range', 'medium_term')
    
    token = TokenService.decrypt_token(current_user.access_token)
    service = SpotifyService(token)
    
    try:
        data = service.get_top_artists(limit=limit, time_range=time_range)
        items = data.get('items', [])
        result = []
        for item in items:
            images = item.get('images', [])
            result.append({
                'id': item['id'],
                'name': item['name'],
                'image_url': images[0]['url'] if images else '',
                'followers': item.get('followers', {}).get('total', 0),
                'genres': item.get('genres', [])
            })
        return jsonify(result)
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
