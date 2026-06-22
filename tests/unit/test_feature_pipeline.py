import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.ml.feature_pipeline import FeaturePipeline


def test_build_user_feature_vector():
    """Test feature vector construction with mocked Spotify API."""
    mock_track = {
        'id': 'track1',
        'danceability': 0.5,
        'energy': 0.6,
        'valence': 0.7,
        'tempo': 120,
        'acousticness': 0.1,
        'instrumentalness': 0.0,
        'liveness': 0.2,
        'speechiness': 0.1
    }

    with patch('app.ml.feature_pipeline.SpotifyService') as MockSpotify:
        mock_spotify = MagicMock()
        mock_spotify.get_top_tracks.return_value = {'items': [{'id': 'track1'}]}
        mock_spotify._make_request.return_value = mock_track
        MockSpotify.return_value = mock_spotify

        features = FeaturePipeline.build_user_feature_vector(1, 'test_token')
        assert isinstance(features, list)
        assert len(features) == 8  # 8 audio features


def test_normalize_features():
    """Test feature normalization."""
    features = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    normalized = FeaturePipeline.normalize_features(features)
    assert isinstance(normalized, list)
    assert len(normalized) == len(features)
