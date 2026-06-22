from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.recommendation_service import RecommendationService


@login_required
def get_explore_content():
    """Get explore content for swipe interface."""
    limit = request.args.get('limit', 10, type=int)
    items = RecommendationService.get_explore_content(current_user.id, limit)
    
    # Convert Spotify API items to frontend format
    result = []
    for item in items:
        if isinstance(item, dict) and 'id' in item:
            # Spotify track object
            album_images = item.get('album', {}).get('images', []) if item.get('album') else []
            artists = item.get('artists', [])
            result.append({
                'id': item['id'],
                'name': item.get('name', 'Unknown'),
                'image_url': album_images[0]['url'] if album_images else '',
                'artist': artists[0].get('name', 'Unknown') if artists else 'Unknown'
            })
        elif isinstance(item, dict) and 'track' in item:
            # Spotify album item with track wrapper
            track = item['track']
            album_images = track.get('album', {}).get('images', []) if track.get('album') else []
            artists = track.get('artists', [])
            result.append({
                'id': track.get('id', ''),
                'name': track.get('name', 'Unknown'),
                'image_url': album_images[0]['url'] if album_images else '',
                'artist': artists[0].get('name', 'Unknown') if artists else 'Unknown'
            })
        elif isinstance(item, dict) and 'images' in item:
            # Album-like item from fallback
            artists = item.get('artists', [])
            result.append({
                'id': item.get('id', ''),
                'name': item.get('name', 'Unknown'),
                'image_url': item.get('image_url', ''),
                'artist': artists[0].get('name', 'Unknown') if isinstance(artists, list) and artists else item.get('artist', 'Unknown')
            })
    
    return jsonify(result)


@login_required
def submit_swipe():
    """Submit swipe action (like/dislike)."""
    data = request.get_json()
    content_id = data.get('content_id')
    liked = data.get('liked', False)
    
    RecommendationService.record_swipe(current_user.id, content_id, liked)
    return jsonify({'message': 'Swipe recorded successfully'})
