# app/views/main.py — Landing, about, support, and home page routes

from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('landing.html')


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@main_bp.route('/support')
def support():
    """Support page."""
    return render_template('support.html')


@main_bp.route('/home')
@login_required
def home():
    """Home page for authenticated users."""
    return render_template('fyp.html')
