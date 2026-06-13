"""
Pytest fixtures for CarbonCredit tests.

Provides:
    - test_app: Flask app configured for testing
    - client: Test client for making HTTP requests
    - test_user: Pre-created user for authenticated tests
    - auth_client: Authenticated test client
"""

import pytest
from app import create_app
from models import db as _db, User


@pytest.fixture(scope="function")
def test_app():
    """Create a Flask application configured for testing."""
    app = create_app("testing")

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture(scope="function")
def test_user(test_app):
    """Create a test user in the database."""
    with test_app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
        )
        user.set_password("TestPass123!")
        _db.session.add(user)
        _db.session.commit()
        yield user


@pytest.fixture(scope="function")
def auth_client(client):
    """Create an authenticated test client (automatically authenticated via guest auto-login)."""
    return client
