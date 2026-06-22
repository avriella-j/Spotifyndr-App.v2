# app/tasks/ml_tasks.py — Celery tasks for ML model training

from app.tasks.celery_app import celery
from app.models.user import User
from app.models.user_feature_vector import UserFeatureVector
from app.models.user_similarity import UserSimilarity
from app.ml.feature_pipeline import FeaturePipeline
from app.ml.logistic_regression import LogisticRegressionModel
from app.ml.knn_similarity import KNNSimilarity
from app.ml.model_store import ModelStore
from app.services.token_service import TokenService
from app.extensions import db
import numpy as np


@celery.task
# Build feature vector and retrain LR model for a specific user
def retrain_user_model(user_id):
    """Retrain ML model for a specific user."""
    user = User.query.get(user_id)
    if not user:
        return
    
    # Build feature vector
    access_token = TokenService.decrypt_token(user.access_token)
    features = FeaturePipeline.build_user_feature_vector(user_id, access_token)
    features = FeaturePipeline.normalize_features(features)
    
    # Store feature vector
    feature_vector = UserFeatureVector.query.filter_by(user_id=user_id).first()
    if not feature_vector:
        feature_vector = UserFeatureVector(user_id=user_id)
        db.session.add(feature_vector)
    
    feature_vector.features = features
    db.session.commit()
    
    # Train and save model
    model = LogisticRegressionModel()
    # In real implementation, would use historical data
    # model.train(X, y)
    ModelStore.save_model(model, 'lr_model', user_id)
    
    return {'status': 'success', 'user_id': user_id}


@celery.task
# Retrain global LR model using all user feature vectors
def retrain_global_model():
    """Retrain global ML model."""
    # Get all user feature vectors
    feature_vectors = UserFeatureVector.query.all()
    
    if len(feature_vectors) < 10:
        return {'status': 'insufficient_data'}
    
    # Prepare training data
    X = np.array([fv.features for fv in feature_vectors])
    # In real implementation, would have labels
    # y = ...
    
    # Train model
    model = LogisticRegressionModel()
    # model.train(X, y)
    
    ModelStore.save_model(model, 'global_lr_model')
    
    return {'status': 'success'}


@celery.task
# Fit KNN model and update similarity scores for all users
def knn_fit():
    """Fit KNN model for user similarity."""
    # Get all user feature vectors
    feature_vectors = UserFeatureVector.query.all()
    
    if len(feature_vectors) < 2:
        return {'status': 'insufficient_data'}
    
    X = np.array([fv.features for fv in feature_vectors])
    user_ids = [fv.user_id for fv in feature_vectors]
    
    # Fit KNN model
    knn = KNNSimilarity(n_neighbors=10)
    knn.fit(X, user_ids)
    
    ModelStore.save_model(knn, 'knn_model')
    
    # Update similarity scores in database
    for i, fv in enumerate(feature_vectors):
        similar_users = knn.find_similar(fv.features, k=5)
        for similar in similar_users:
            user_id_1 = fv.user_id
            user_id_2 = similar['user_id']
            score = similar['similarity_score']
            
            from app.services.similarity_service import SimilarityService
            SimilarityService.update_similarity(user_id_1, user_id_2, score)
    
    return {'status': 'success'}
