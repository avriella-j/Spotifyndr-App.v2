from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.user_service import UserService


@login_required
def get_settings():
    """Get user settings."""
    settings = UserService.get_user_settings(current_user.id)
    return jsonify(settings)


@login_required
def update_settings():
    """Update user settings."""
    data = request.get_json()
    settings = UserService.update_user_settings(current_user.id, data)
    return jsonify(settings)
