# app/views/explore.py — Explore (swipe) page route

from flask import Blueprint, render_template
from flask_login import login_required

explore_bp = Blueprint('explore', __name__)


@explore_bp.route('/')
@login_required
def explore():
    """Explore page."""
    return render_template('explore.html')
