import pytest
from unittest.mock import patch, MagicMock
from app.ml.feature_pipeline import FeaturePipeline
from app.ml.logistic_regression import LogisticRegressionModel


def test_recommendation_pipeline():
    """Test end-to-end recommendation pipeline with mocked Spotify API."""
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
        mock_spotify.get_top_artists.return_value = {'items': []}
        mock_spotify._make_request.return_value = mock_track
        MockSpotify.return_value = mock_spotify

        # Build feature vector
        features = FeaturePipeline.build_user_feature_vector(1, 'test_token')
        assert len(features) == 8

        # Normalize features
        normalized = FeaturePipeline.normalize_features(features)
        assert len(normalized) == 8

    # Train model (placeholder)
    model = LogisticRegressionModel()
    assert model.is_trained is False
