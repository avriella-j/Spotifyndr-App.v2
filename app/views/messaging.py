# app/views/messaging.py — Messaging inbox page route

from flask import Blueprint, render_template
from flask_login import login_required

messaging_bp = Blueprint('messaging', __name__)


@messaging_bp.route('/')
@login_required
def messaging():
    """Messaging page."""
    return render_template('messaging.html')
