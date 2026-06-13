"""
SQLAlchemy database models for CarbonCredit.

Models:
    - User: Authentication and profile data
    - CarbonEntry: Daily carbon footprint records
    - Badge: Gamification achievements
"""

import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    """User model with secure password hashing."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    entries = db.relationship(
        "CarbonEntry", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    badges = db.relationship(
        "Badge", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and store password using bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verify password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class CarbonEntry(db.Model):
    """Daily carbon footprint entry with category breakdown."""

    __tablename__ = "carbon_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    date = db.Column(db.Date, nullable=False, index=True)

    # CO₂e values in kg
    transport_co2 = db.Column(db.Float, nullable=False, default=0.0)
    energy_co2 = db.Column(db.Float, nullable=False, default=0.0)
    food_co2 = db.Column(db.Float, nullable=False, default=0.0)
    waste_co2 = db.Column(db.Float, nullable=False, default=0.0)
    water_co2 = db.Column(db.Float, nullable=False, default=0.0)
    total_co2 = db.Column(db.Float, nullable=False, default=0.0)

    # Raw input data stored as JSON for drill-down views
    details_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def set_details(self, details_dict):
        """Serialize input details to JSON."""
        self.details_json = json.dumps(details_dict)

    def get_details(self):
        """Deserialize input details from JSON."""
        if self.details_json:
            return json.loads(self.details_json)
        return {}

    @property
    def category_breakdown(self):
        """Return category breakdown as a dictionary."""
        return {
            "transport": round(self.transport_co2, 2),
            "energy": round(self.energy_co2, 2),
            "food": round(self.food_co2, 2),
            "waste": round(self.waste_co2, 2),
            "water": round(self.water_co2, 2),
        }

    def __repr__(self):
        return f"<CarbonEntry {self.date} - {self.total_co2:.2f} kg CO₂e>"


class Badge(db.Model):
    """Gamification badge awarded to users for achievements."""

    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    badge_type = db.Column(db.String(50), nullable=False)
    earned_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Unique constraint: a user can earn each badge type only once
    __table_args__ = (
        db.UniqueConstraint("user_id", "badge_type", name="uq_user_badge"),
    )

    # Badge metadata
    BADGE_INFO = {
        "first_entry": {
            "name": "First Step",
            "description": "Logged your first carbon footprint entry",
            "icon": "🌱",
        },
        "week_streak": {
            "name": "Consistency Champion",
            "description": "Logged entries for 7 consecutive days",
            "icon": "🔥",
        },
        "low_carbon_day": {
            "name": "Low Carbon Day",
            "description": "Achieved a daily footprint under 5 kg CO₂e",
            "icon": "🌿",
        },
        "green_commuter": {
            "name": "Green Commuter",
            "description": "Used public transport or cycling for a week",
            "icon": "🚲",
        },
        "eco_warrior": {
            "name": "Eco Warrior",
            "description": "Maintained below-average footprint for 30 days",
            "icon": "🛡️",
        },
    }

    @property
    def info(self):
        """Get badge display metadata."""
        return self.BADGE_INFO.get(
            self.badge_type,
            {"name": self.badge_type, "description": "", "icon": "🏅"},
        )

    def __repr__(self):
        return f"<Badge {self.badge_type} for User {self.user_id}>"
