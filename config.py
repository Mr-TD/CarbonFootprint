"""
Application configuration classes.

Supports Development, Testing, and Production environments.
Security-sensitive values are loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration with secure defaults."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 604800  # 7 days in seconds

    # Rate limiting defaults
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "200 per hour"

    # WTF CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///carboncredit.db"
    )
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class TestingConfig(BaseConfig):
    """Testing configuration with in-memory database."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Disable CSRF for test forms
    SESSION_COOKIE_SECURE = False
    LOGIN_DISABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(BaseConfig):
    """Production configuration with strict security."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///carboncredit.db"
    )
    SESSION_COOKIE_SECURE = True  # Requires HTTPS


# Configuration map for easy selection
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
