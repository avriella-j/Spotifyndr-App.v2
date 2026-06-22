from flask import jsonify
from flask_login import login_required, current_user
from app.services.follow_service import FollowService


@login_required
def follow_user(user_id):
    """Follow a user."""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    FollowService.follow_user(current_user.id, user_id)
    return jsonify({'message': 'User followed successfully'})


@login_required
def unfollow_user(user_id):
    """Unfollow a user."""
    FollowService.unfollow_user(current_user.id, user_id)
    return jsonify({'message': 'User unfollowed successfully'})


@login_required
def get_followers(user_id):
    """Get user's followers."""
    followers = FollowService.get_followers(user_id)
    return jsonify([f.follower.to_dict() for f in followers])


@login_required
def get_following(user_id):
    """Get users that user is following."""
    following = FollowService.get_following(user_id)
    return jsonify([f.followed.to_dict() for f in following])
