from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.recommendation_service import RecommendationService


@login_required
def get_recommendations():
    """Get personalized recommendations for FYP."""
    limit = request.args.get('limit', 10, type=int)
    items = RecommendationService.get_user_recommendations(current_user.id, limit)
    
    # Convert Spotify API items to frontend format
    result = []
    for item in items:
        if isinstance(item, dict) and 'id' in item:
            album_images = item.get('album', {}).get('images', []) if item.get('album') else []
            artists = item.get('artists', [])
            result.append({
                'id': item['id'],
                'name': item.get('name', 'Unknown'),
                'image_url': album_images[0]['url'] if album_images else '',
                'artist': artists[0].get('name', 'Unknown') if artists else 'Unknown'
            })
    
    return jsonify(result)


@login_required
def submit_feedback(rec_id):
    """Submit feedback on a recommendation."""
    data = request.get_json()
    liked = data.get('liked', False)
    
    RecommendationService.submit_feedback(current_user.id, rec_id, liked)
    return jsonify({'message': 'Feedback submitted successfully'})
