# app/views/profile.py — User profile page routes

from flask import Blueprint, render_template
from flask_login import login_required, current_user

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/')
@login_required
def profile():
    """Profile page."""
    return render_template('profile.html')


@profile_bp.route('/<int:user_id>')
@login_required
def user_profile(user_id):
    """View another user's profile."""
    return render_template('profile.html', user_id=user_id)
