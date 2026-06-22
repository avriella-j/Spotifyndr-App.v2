# app/ml/feature_pipeline.py — Feature engineering from Spotify data

import numpy as np
from app.services.spotify_service import SpotifyService


class FeaturePipeline:
    """Feature vector construction for ML models."""
    
    @staticmethod
    # Extract audio features from top tracks and aggregate into vector
    def build_user_feature_vector(user_id, access_token):
        """Build feature vector from user's Spotify data."""
        spotify = SpotifyService(access_token)
        
        # Get top tracks and artists
        top_tracks = spotify.get_top_tracks(limit=50)
        top_artists = spotify.get_top_artists(limit=50)
        
        # Extract audio features from tracks
        features = []
        
        for track in top_tracks.get('items', []):
            track_id = track['id']
            audio_features = spotify._make_request(f'/audio-features/{track_id}')
            
            if audio_features:
                feature_vector = [
                    audio_features.get('danceability', 0),
                    audio_features.get('energy', 0),
                    audio_features.get('valence', 0),
                    audio_features.get('tempo', 0) / 200,  # Normalized
                    audio_features.get('acousticness', 0),
                    audio_features.get('instrumentalness', 0),
                    audio_features.get('liveness', 0),
                    audio_features.get('speechiness', 0)
                ]
                features.append(feature_vector)
        
        # Aggregate features (mean)
        if features:
            feature_array = np.array(features)
            aggregated = np.mean(feature_array, axis=0)
            return aggregated.tolist()
        
        return [0] * 8  # Default zero vector
    
    @staticmethod
    def normalize_features(features):
        """Normalize feature vector."""
        features = np.array(features)
        mean = np.mean(features)
        std = np.std(features)
        
        if std > 0:
            return ((features - mean) / std).tolist()
        return features.tolist()
