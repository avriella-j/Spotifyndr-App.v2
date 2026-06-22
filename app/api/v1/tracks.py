from flask import jsonify
from flask_login import login_required, current_user
from app.services.spotify_service import SpotifyService
from app.services.token_service import TokenService


@login_required
def get_track(track_id):
    """Get a track's details from Spotify."""
    token = TokenService.decrypt_token(current_user.access_token)
    service = SpotifyService(token)

    try:
        data = service.get_track(track_id)
        album_images = data.get('album', {}).get('images', [])
        artists = data.get('artists', [])
        return jsonify({
            'id': data['id'],
            'name': data['name'],
            'artist': artists[0]['name'] if artists else 'Unknown',
            'image_url': album_images[0]['url'] if album_images else '',
            'album': data.get('album', {}).get('name', ''),
            'popularity': data.get('popularity', 0),
            'preview_url': data.get('preview_url', ''),
            'duration_ms': data.get('duration_ms', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
