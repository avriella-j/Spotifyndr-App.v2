# app/views/detail.py — Song, artist, and user detail page routes

from flask import Blueprint, render_template
from flask_login import login_required, current_user

detail_bp = Blueprint('detail', __name__)


@detail_bp.route('/song/<song_id>')
@login_required
def song_detail(song_id):
    """Song detail page."""
    # TODO: Fetch song data from Spotify API or database
    song = {
        'name': 'Song Name',
        'artist_name': 'Artist Name',
        'album_name': 'Album Name',
        'image_url': '/static/img/default-album.svg',
        'duration_ms': 180000,
        'popularity': 75
    }
    return render_template('song.html', song=song)


@detail_bp.route('/artist/<artist_id>')
@login_required
def artist_detail(artist_id):
    """Artist detail page."""
    # TODO: Fetch artist data from Spotify API or database
    artist = {
        'name': 'Artist Name',
        'image_url': '/static/img/default-artist.svg',
        'followers': 1000000,
        'genres': ['Pop', 'Rock']
    }
    return render_template('artist.html', artist=artist)


@detail_bp.route('/user/<user_id>')
@login_required
def user_detail(user_id):
    """User profile page (viewing another user)."""
    # TODO: Fetch user data from database
    user = {
        'display_name': 'User Name',
        'email': 'user@example.com',
        'image_url': '/static/img/default-avatar.svg',
        'followers_count': 100,
        'following_count': 50
    }
    return render_template('user_profile.html', user=user)
