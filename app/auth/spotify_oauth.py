# app/auth/spotify_oauth.py — Spotify OAuth Authorization Code Flow impl

import base64
import secrets
import time
import requests
from flask import current_app
from urllib.parse import urlencode


class SpotifyOAuth:
    """Spotify OAuth implementation (Authorization Code Flow)."""

    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_URL = 'https://api.spotify.com/v1'

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def _get_config(self):
        """Get config values from current app if not set during init."""
        if not self.client_id:
            self.client_id = current_app.config['SPOTIFY_CLIENT_ID']
        if not self.client_secret:
            self.client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']
        if not self.redirect_uri:
            self.redirect_uri = current_app.config['SPOTIFY_REDIRECT_URI']

    def get_authorization_url(self):
        """Generate authorization URL."""
        self._get_config()
        state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'user-read-private user-read-email user-top-read user-library-read',
            'state': state
        }

        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        return auth_url, state

    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        self._get_config()
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.TOKEN_URL, data=data, headers=headers)

        if not response.ok:
            app = current_app._get_current_object()

            app.logger.error(
                f"Spotify token error {response.status_code}"
            )

            app.logger.error(
                f"Redirect URI: {self.redirect_uri}"
            )

            app.logger.error(
                f"Response body: {response.text}"
            )

        response.raise_for_status()

        token_data = response.json()
        token_data['expires_at'] = int(time.time()) + token_data['expires_in']

        return token_data

    # Refresh an expired access token
    def refresh_access_token(self, refresh_token):
        """Refresh access token."""
        self._get_config()
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        token_data['expires_at'] = int(time.time()) + token_data['expires_in']

        return token_data

    # Fetch user profile from Spotify /me endpoint
    def get_user_profile(self, access_token):
        """Get user profile from Spotify API."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'{self.API_URL}/me', headers=headers)
        response.raise_for_status()
        return response.json()