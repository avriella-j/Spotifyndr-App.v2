import pytest
from app import create_app
from app.extensions import db
from app.config import config


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_spotify_response(monkeypatch):
    """Mock Spotify API responses."""
    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {'items': []}
        return MockResponse()
    
    monkeypatch.setattr('requests.get', mock_get)
