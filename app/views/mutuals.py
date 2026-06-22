# app/views/mutuals.py — Find Mutuals page route

from flask import Blueprint, render_template
from flask_login import login_required

mutuals_bp = Blueprint('mutuals', __name__)


@mutuals_bp.route('/')
@login_required
def mutuals():
    """Find Mutuals page."""
    return render_template('mutuals.html')
