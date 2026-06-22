import pytest
import numpy as np
from app.ml.knn_similarity import KNNSimilarity


def test_knn_output_format():
    """Test KNN output format is correct."""
    knn = KNNSimilarity(n_neighbors=5)
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    user_ids = [1, 2, 3]
    
    knn.fit(X, user_ids)
    similar = knn.find_similar([1, 2, 3], k=2)
    
    assert isinstance(similar, list)
    assert all('user_id' in item for item in similar)
    assert all('similarity_score' in item for item in similar)
    assert all(0 <= item['similarity_score'] <= 1 for item in similar)
