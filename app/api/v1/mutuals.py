from flask import jsonify
from flask_login import login_required, current_user
from app.services.similarity_service import SimilarityService


@login_required
def find_mutuals():
    """Find users with similar music taste."""
    limit = 10
    mutuals = SimilarityService.find_similar_users(current_user.id, limit)
    return jsonify([m.to_dict() for m in mutuals])
