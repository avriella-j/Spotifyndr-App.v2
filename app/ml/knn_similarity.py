# app/ml/knn_similarity.py — KNN model for user similarity scoring

import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib


class KNNSimilarity:
    """KNN fitting + similarity scoring."""
    
    def __init__(self, n_neighbors=10):
        self.n_neighbors = n_neighbors
        self.model = NearestNeighbors(n_neighbors=n_neighbors)
        self.is_fitted = False
        self.user_ids = None
    
    def fit(self, feature_vectors, user_ids):
        """Fit KNN model on user feature vectors."""
        self.model.fit(feature_vectors)
        self.user_ids = np.array(user_ids)
        self.is_fitted = True
    
    # Find k nearest neighbors, exclude self, return scores
    def find_similar(self, user_feature_vector, k=None):
        """Find k most similar users."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before finding similar users")
        
        k = k or self.n_neighbors
        distances, indices = self.model.kneighbors([user_feature_vector], n_neighbors=k+1)
        
        # Skip the first result (it's the user themselves)
        similar_indices = indices[0][1:k+1]
        similar_distances = distances[0][1:k+1]
        
        similar_users = []
        for idx, dist in zip(similar_indices, similar_distances):
            similar_users.append({
                'user_id': int(self.user_ids[idx]),
                'similarity_score': float(1 / (1 + dist))  # Convert distance to similarity
            })
        
        return similar_users
    
    def save(self, filepath):
        """Save model to file."""
        joblib.dump({
            'model': self.model,
            'user_ids': self.user_ids,
            'n_neighbors': self.n_neighbors
        }, filepath)
    
    def load(self, filepath):
        """Load model from file."""
        data = joblib.load(filepath)
        self.model = data['model']
        self.user_ids = data['user_ids']
        self.n_neighbors = data['n_neighbors']
        self.is_fitted = True
