# app/services/token_service.py — Token encryption/decryption service

from cryptography.fernet import Fernet
import os


class TokenService:
    """Encrypt/decrypt tokens, refresh logic."""

    _cached_key = None

    @staticmethod
    # Get or cache encryption key from env
    def get_key():
        """Get encryption key from environment or generate one."""
        if TokenService._cached_key is not None:
            return TokenService._cached_key

        key = os.environ.get('TOKEN_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
        TokenService._cached_key = key if isinstance(key, bytes) else key.encode()
        return TokenService._cached_key

    @staticmethod
    # Create Fernet cipher with cached key
    def get_cipher():
        """Get Fernet cipher instance."""
        return Fernet(TokenService.get_key())
    
    @staticmethod
    def encrypt_token(token):
        """Encrypt a token."""
        cipher = TokenService.get_cipher()
        return cipher.encrypt(token.encode()).decode()
    
    @staticmethod
    def decrypt_token(encrypted_token):
        """Decrypt a token."""
        cipher = TokenService.get_cipher()
        return cipher.decrypt(encrypted_token.encode()).decode()
    
    @staticmethod
    # Compare expiry datetime with current time
    def is_token_expired(expires_at):
        """Check if token is expired."""
        from datetime import datetime
        return datetime.utcnow() > expires_at
