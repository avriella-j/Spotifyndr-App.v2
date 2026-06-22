import pytest
from app.services.token_service import TokenService


def test_encrypt_decrypt_token():
    """Test token encryption and decryption."""
    original_token = 'test_access_token_12345'
    
    encrypted = TokenService.encrypt_token(original_token)
    assert encrypted != original_token
    
    decrypted = TokenService.decrypt_token(encrypted)
    assert decrypted == original_token


def test_is_token_expired():
    """Test token expiration check."""
    from datetime import datetime, timedelta
    
    # Expired token
    expired_time = datetime.utcnow() - timedelta(hours=1)
    assert TokenService.is_token_expired(expired_time) is True
    
    # Valid token
    valid_time = datetime.utcnow() + timedelta(hours=1)
    assert TokenService.is_token_expired(valid_time) is False
