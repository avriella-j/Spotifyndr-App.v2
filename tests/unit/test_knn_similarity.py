import pytest
import numpy as np
from app.ml.knn_similarity import KNNSimilarity


def test_knn_initialization():
    """Test KNN initialization."""
    knn = KNNSimilarity(n_neighbors=5)
    assert knn.n_neighbors == 5
    assert knn.is_fitted is False


def test_knn_fitting():
    """Test KNN fitting."""
    knn = KNNSimilarity(n_neighbors=5)
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    user_ids = [1, 2, 3]
    
    knn.fit(X, user_ids)
    assert knn.is_fitted is True


def test_knn_find_similar():
    """Test finding similar users."""
    knn = KNNSimilarity(n_neighbors=5)
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    user_ids = [1, 2, 3]
    
    knn.fit(X, user_ids)
    similar = knn.find_similar([1, 2, 3], k=2)
    assert len(similar) == 2
    assert 'user_id' in similar[0]
    assert 'similarity_score' in similar[0]
