"""
CarbonCredit — Flask Application Factory.

A portal for calculating, tracking, and reducing your daily carbon footprint.
Built with Flask, SQLAlchemy, and secure by default.
"""

import os
from flask import Flask, render_template
from flask_login import LoginManager, login_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config_map
from models import db, bcrypt, User


# Extensions (initialized here, bound to app in factory)
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)


def create_app(config_name=None):
    """
    Application factory pattern.

    Args:
        config_name: Configuration to use ('development', 'testing', 'production')

    Returns:
        Configured Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["development"]))

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Flask-Login configuration (no login view redirects since we auto-authenticate)
    login_manager.login_view = None

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))

    @app.before_request
    def auto_login_guest():
        """Automatically log in a default guest user if not authenticated."""
        # Check if DB is initialized (useful during testing/setup)
        try:
            if not current_user.is_authenticated:
                guest = User.query.filter_by(username="Guest").first()
                if not guest:
                    guest = User(
                        username="Guest",
                        email="guest@carboncredit.local",
                    )
                    guest.set_password("guest-dummy-password")
                    db.session.add(guest)
                    db.session.commit()
                login_user(guest, remember=True)
        except Exception:
            # Fallback for database setup/migrations/errors
            db.session.rollback()

    # Register blueprints
    from routes.calculator import calculator_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp

    app.register_blueprint(calculator_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Landing page route
    @app.route("/")
    def index():
        """Landing page."""
        return render_template("index.html")

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template("base.html", error_code=404, error_message="Page not found"), 404

    @app.errorhandler(429)
    def rate_limited(error):
        """Handle rate limit exceeded."""
        return render_template("base.html", error_code=429, error_message="Too many requests. Please slow down."), 429

    @app.errorhandler(500)
    def server_error(error):
        """Handle internal server errors."""
        return render_template("base.html", error_code=500, error_message="Something went wrong. Please try again."), 500

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


# Entry point for development
if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, host="127.0.0.1", port=5000)
