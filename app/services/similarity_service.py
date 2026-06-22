# app/services/similarity_service.py — User similarity queries

from app.models.user_similarity import UserSimilarity
from app.models.user import User
from app.extensions import db


class SimilarityService:
    """KNN computation and user similarity."""
    
    @staticmethod
    def find_similar_users(user_id, limit=10):
        """Find users with similar music taste."""
        similarities = UserSimilarity.query.filter_by(user_id_1=user_id).order_by(
            UserSimilarity.similarity_score.desc()
        ).limit(limit).all()
        
        similar_users = []
        for sim in similarities:
            user = User.query.get(sim.user_id_2)
            if user:
                similar_users.append(user)
        
        return similar_users
    
    @staticmethod
    # Calculate similarity score between two users
    def compute_similarity(user_id_1, user_id_2):
        """Compute similarity between two users."""
        # Placeholder: return random similarity score
        # In real implementation, this would use ML models
        import random
        return random.random()
    
    @staticmethod
    def update_similarity(user_id_1, user_id_2, score):
        """Update similarity score between two users."""
        # Ensure user_id_1 < user_id_2 for consistency
        if user_id_1 > user_id_2:
            user_id_1, user_id_2 = user_id_2, user_id_1
        
        similarity = UserSimilarity.query.filter_by(
            user_id_1=user_id_1,
            user_id_2=user_id_2
        ).first()
        
        if similarity:
            similarity.similarity_score = score
        else:
            similarity = UserSimilarity(
                user_id_1=user_id_1,
                user_id_2=user_id_2,
                similarity_score=score
            )
            db.session.add(similarity)
        
        db.session.commit()
