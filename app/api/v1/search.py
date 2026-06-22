from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.spotify_service import SpotifyService
from app.services.token_service import TokenService
from app.services.user_service import UserService


@login_required
def search():
    """General search across users and Spotify tracks."""
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    results = []

    # Search users by display name
    users = UserService.search_users(q)
    for u in users:
        results.append({
            'id': f'user_{u.id}',
            'name': u.display_name,
            'image_url': u.image_url or '',
            'type': 'user'
        })

    # Search Spotify tracks
    try:
        token = TokenService.decrypt_token(current_user.access_token)
        service = SpotifyService(token)
        data = service.search(q, type='track', limit=5)
        for item in data.get('tracks', {}).get('items', []):
            album_images = item.get('album', {}).get('images', [])
            artists = item.get('artists', [])
            results.append({
                'id': item['id'],
                'name': item['name'],
                'image_url': album_images[0]['url'] if album_images else '',
                'type': 'track',
                'artist': artists[0]['name'] if artists else 'Unknown'
            })
    except Exception:
        pass

    return jsonify(results)
