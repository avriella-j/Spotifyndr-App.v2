# app/services/token_service.py — Token encryption/decryption + refresh-aware access
from datetime import datetime, timezone
from cryptography.fernet import Fernet
import os


class TokenService:
    """Encrypt/decrypt tokens, refresh logic."""
    _cached_key = None

    @staticmethod
    def get_key():
        """Get encryption key from environment. Raises if missing."""
        if TokenService._cached_key is not None:
            return TokenService._cached_key
        key = os.environ.get('TOKEN_ENCRYPTION_KEY')
        if not key:
            raise RuntimeError(
                "TOKEN_ENCRYPTION_KEY is not set in the environment. "
                "Generate one with `python -c \"from cryptography.fernet import "
                "Fernet; print(Fernet.generate_key().decode())\"` and put it in .env."
            )
        TokenService._cached_key = key if isinstance(key, bytes) else key.encode()
        return TokenService._cached_key

    @staticmethod
    def get_cipher():
        return Fernet(TokenService.get_key())

    @staticmethod
    def encrypt_token(token):
        cipher = TokenService.get_cipher()
        return cipher.encrypt(token.encode()).decode()

    @staticmethod
    def decrypt_token(encrypted_token):
        cipher = TokenService.get_cipher()
        return cipher.decrypt(encrypted_token.encode()).decode()

    @staticmethod
    def is_token_expired(expires_at):
        """Check if token is expired (with 60s safety buffer)."""
        if expires_at is None:
            return True
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            now = datetime.utcnow()
        return now >= expires_at

    @staticmethod
    def get_valid_access_token(user):
        """
        Return a decrypted, guaranteed-valid access token for this user.
        Refreshes from Spotify and updates the DB if the stored token is
        expired. ALL other code must call this instead of reading
        user.access_token directly.
        """
        from app.auth.spotify_oauth import SpotifyOAuth
        from app.extensions import db

        if TokenService.is_token_expired(user.token_expires_at):
            oauth = SpotifyOAuth()
            refresh_token = TokenService.decrypt_token(user.refresh_token)
            token_data = oauth.refresh_access_token(refresh_token)

            user.access_token = TokenService.encrypt_token(token_data['access_token'])
            if 'refresh_token' in token_data:
                user.refresh_token = TokenService.encrypt_token(token_data['refresh_token'])
            user.token_expires_at = datetime.utcfromtimestamp(token_data['expires_at'])
            db.session.commit()

            return token_data['access_token']

        return TokenService.decrypt_token(user.access_token)
