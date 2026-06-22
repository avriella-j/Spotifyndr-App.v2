# app/services/recommendation_service.py — Recommendation and swipe logic

from app.models.recommendation_event import RecommendationEvent
from app.models.swipe import Swipe
from app.models.user import User
from app.extensions import db
from app.services.token_service import TokenService
from app.services.spotify_service import SpotifyService


class RecommendationService:
    """Recommendation logic using Spotify API data."""
    
    @staticmethod
    def get_user_recommendations(user_id, limit=10):
        """Get personalized recommendations for FYP — fetches top tracks from Spotify."""
        user = User.query.get(user_id)
        if not user or not user.access_token:
            return []
        
        try:
            token = TokenService.decrypt_token(user.access_token)
            service = SpotifyService(token)
            data = service.get_top_tracks(limit=limit, time_range='medium_term')
            return data.get('items', [])
        except Exception:
            return []
    
    @staticmethod
    # Mark a recommendation as liked/disliked
    def submit_feedback(user_id, rec_id, liked):
        """Submit feedback on a recommendation."""
        rec = RecommendationEvent.query.get(rec_id)
        if not rec:
            return
        
        rec.feedback = liked
        db.session.commit()
    
    @staticmethod
    def get_explore_content(user_id, limit=10):
        """Get explore content for swipe interface — fetches recommended tracks from Spotify."""
        user = User.query.get(user_id)
        if not user or not user.access_token:
            return []
        
        try:
            token = TokenService.decrypt_token(user.access_token)
            service = SpotifyService(token)
            
            # Get user's top artists to find similar content
            top_data = service.get_top_artists(limit=5, time_range='medium_term')
            top_artists = top_data.get('items', [])
            
            if top_artists:
                # Use first artist to get recommendations
                artist_id = top_artists[0]['id']
                rec_data = service._make_request(f'/recommendations?seed_artists={artist_id}&limit={limit}')
                return rec_data.get('tracks', [])
            
            # Fallback: return top tracks
            fallback = service.get_top_tracks(limit=limit, time_range='short_term')
            return fallback.get('items', [])
        except Exception:
            # Final fallback: return new releases
            try:
                token = TokenService.decrypt_token(user.access_token)
                service = SpotifyService(token)
                new_data = service._make_request('/browse/new-releases?limit=' + str(limit))
                albums = new_data.get('albums', {}).get('items', [])
                # Convert albums to track-like objects
                result = []
                for album in albums:
                    images = album.get('images', [])
                    artists = album.get('artists', [])
                    result.append({
                        'id': album['id'],
                        'name': album['name'],
                        'artist': artists[0]['name'] if artists else 'Unknown',
                        'image_url': images[0]['url'] if images else '',
                        'album': album['name']
                    })
                return result
            except Exception:
                return []
    
    @staticmethod
    def record_swipe(user_id, content_id, liked):
        """Record swipe action."""
        swipe = Swipe(
            user_id=user_id,
            content_id=content_id,
            content_type='track',
            liked=liked
        )
        db.session.add(swipe)
        db.session.commit()
