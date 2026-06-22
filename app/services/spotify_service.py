# app/services/spotify_service.py — Spotify Web API client with caching

import requests
import time
from flask import current_app
from app.models.spotify_cache import SpotifyCache
from app.extensions import db


class SpotifyService:
    """Spotify Web API client with rate limiting and caching."""
    
    API_URL = 'https://api.spotify.com/v1'
    RATE_LIMIT_DELAY = 0.1  # 100ms between requests
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _get_headers(self):
        """Get request headers with authorization."""
        return {'Authorization': f'Bearer {self.access_token}'}
    
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to Spotify API."""
        self._rate_limit()
        
        cache_key = f"{endpoint}:{str(params)}"
        cached = SpotifyCache.query.filter_by(cache_key=cache_key).first()
        
        if cached and cached.expires_at > time.time():
            return cached.data
        
        url = f"{self.API_URL}{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache the response (1 hour TTL)
        cache = SpotifyCache(
            cache_key=cache_key,
            data=data,
            expires_at=time.time() + 3600  # 1 hour cache
        )
        db.session.add(cache)
        db.session.commit()
        
        return data
    
    def get_user_profile(self):
        """Get current user profile."""
        return self._make_request('/me')
    
    def get_top_tracks(self, limit=20, time_range='medium_term'):
        """Get user's top tracks."""
        return self._make_request('/me/top/tracks', {'limit': limit, 'time_range': time_range})
    
    def get_top_artists(self, limit=20, time_range='medium_term'):
        """Get user's top artists."""
        return self._make_request('/me/top/artists', {'limit': limit, 'time_range': time_range})
    
    def get_track(self, track_id):
        """Get track details."""
        return self._make_request(f'/tracks/{track_id}')
    
    def get_artist(self, artist_id):
        """Get artist details."""
        return self._make_request(f'/artists/{artist_id}')
    
    def get_playlist(self, playlist_id):
        """Get playlist details."""
        return self._make_request(f'/playlists/{playlist_id}')
    
    def search(self, query, type='track', limit=10):
        """Search Spotify."""
        return self._make_request('/search', {'q': query, 'type': type, 'limit': limit})
