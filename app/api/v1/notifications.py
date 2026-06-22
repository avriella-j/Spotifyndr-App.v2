from flask import jsonify
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService


@login_required
def get_notifications():
    """Get user's notifications."""
    notifications = NotificationService.get_user_notifications(current_user.id)
    return jsonify([n.to_dict() for n in notifications])


@login_required
def mark_read(notification_id):
    """Mark notification as read."""
    NotificationService.mark_as_read(notification_id)
    return jsonify({'message': 'Notification marked as read'})
