# app/auth/routes.py — Spotify OAuth login/logout routes

from flask import Blueprint, redirect, url_for, session, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.auth.spotify_oauth import SpotifyOAuth
from app.models.user import User
from app.services.user_service import UserService
from app.services.spotify_sync_service import SpotifySyncService

auth_bp = Blueprint('auth', __name__)
spotify_oauth = SpotifyOAuth()


@auth_bp.route('/login')
def login():
    """Initiate Spotify OAuth login flow."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    auth_url, state = spotify_oauth.get_authorization_url()
    session['oauth_state'] = state
    return redirect(auth_url)


@auth_bp.route('/callback')
def callback():
    """Handle Spotify OAuth callback."""
    error = request.args.get('error')
    if error:
        app = current_app._get_current_object()
        app.logger.error(f"Spotify OAuth error: {error}")
        return redirect(url_for('main.index'))

    state = request.args.get('state')
    code = request.args.get('code')

    if not code:
        return redirect(url_for('main.index'))

    if state != session.get('oauth_state'):
        return redirect(url_for('main.index'))

    try:
        token_data = spotify_oauth.get_access_token(code)
        user_data = spotify_oauth.get_user_profile(token_data['access_token'])
    except Exception as e:
        app = current_app._get_current_object()
        app.logger.error(f"Token exchange failed: {e}")
        return redirect(url_for('main.index'))

    user = UserService.get_or_create_user(
        spotify_id=user_data['id'],
        display_name=user_data.get('display_name'),
        email=user_data.get('email'),
        images=user_data.get('images', []),
        access_token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        expires_at=token_data['expires_at']
    )

    login_user(user)
    user_id_for_logging = user.id

    try:
        SpotifySyncService.sync_top_content(user)
    except Exception as e:
        app = current_app._get_current_object()
        app.logger.error(f"Initial Spotify sync failed for user {user_id_for_logging}: {e}")

    return redirect(url_for('profile.profile'))


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user."""
    logout_user()
    return redirect(url_for('main.index'))
