"""
Unit tests for database models.

Tests User, CarbonEntry, and Badge models for
correct behavior, constraints, and relationships.
"""

import pytest
from datetime import date, datetime, timezone
from models import User, CarbonEntry, Badge, db


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, test_app):
        """User should be created with correct attributes."""
        with test_app.app_context():
            user = User(username="testmodel", email="model@test.com")
            user.set_password("TestPass123!")
            db.session.add(user)
            db.session.commit()

            fetched = User.query.filter_by(username="testmodel").first()
            assert fetched is not None
            assert fetched.email == "model@test.com"
            assert fetched.created_at is not None

    def test_password_hashing(self, test_app):
        """Password should be hashed, not stored as plaintext."""
        with test_app.app_context():
            user = User(username="hashtest", email="hash@test.com")
            user.set_password("MySecret123!")
            assert user.password_hash != "MySecret123!"
            assert user.check_password("MySecret123!") is True
            assert user.check_password("WrongPassword") is False

    def test_unique_email_constraint(self, test_app, test_user):
        """Duplicate email should raise an error."""
        with test_app.app_context():
            user2 = User(username="duplicate", email="test@example.com")
            user2.set_password("Pass123!")
            db.session.add(user2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_unique_username_constraint(self, test_app, test_user):
        """Duplicate username should raise an error."""
        with test_app.app_context():
            user2 = User(username="testuser", email="different@test.com")
            user2.set_password("Pass123!")
            db.session.add(user2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_user_repr(self, test_app):
        """User repr should include username."""
        with test_app.app_context():
            user = User(username="reprtest", email="repr@test.com")
            assert "reprtest" in repr(user)


class TestCarbonEntryModel:
    """Tests for the CarbonEntry model."""

    def test_create_entry(self, test_app, test_user):
        """CarbonEntry should be created with correct values."""
        with test_app.app_context():
            entry = CarbonEntry(
                user_id=test_user.id,
                date=date.today(),
                transport_co2=2.5,
                energy_co2=3.0,
                food_co2=2.16,
                waste_co2=0.3,
                water_co2=0.04,
                total_co2=8.0,
            )
            db.session.add(entry)
            db.session.commit()

            fetched = CarbonEntry.query.first()
            assert fetched is not None
            assert fetched.total_co2 == 8.0
            assert fetched.user_id == test_user.id

    def test_details_json(self, test_app, test_user):
        """set_details/get_details should serialize/deserialize correctly."""
        with test_app.app_context():
            entry = CarbonEntry(
                user_id=test_user.id,
                date=date.today(),
                total_co2=5.0,
            )
            details = {"transport_mode": "metro", "distance": 15}
            entry.set_details(details)
            db.session.add(entry)
            db.session.commit()

            fetched = CarbonEntry.query.first()
            retrieved = fetched.get_details()
            assert retrieved["transport_mode"] == "metro"
            assert retrieved["distance"] == 15

    def test_category_breakdown(self, test_app, test_user):
        """category_breakdown property should return correct dict."""
        with test_app.app_context():
            entry = CarbonEntry(
                user_id=test_user.id,
                date=date.today(),
                transport_co2=1.1,
                energy_co2=2.2,
                food_co2=3.3,
                waste_co2=0.4,
                water_co2=0.05,
                total_co2=7.05,
            )
            breakdown = entry.category_breakdown
            assert breakdown["transport"] == 1.1
            assert breakdown["energy"] == 2.2
            assert breakdown["food"] == 3.3

    def test_user_relationship(self, test_app, test_user):
        """Entry should be linked to user via relationship."""
        with test_app.app_context():
            entry = CarbonEntry(
                user_id=test_user.id,
                date=date.today(),
                total_co2=5.0,
            )
            db.session.add(entry)
            db.session.commit()

            user = User.query.get(test_user.id)
            assert user.entries.count() == 1


class TestBadgeModel:
    """Tests for the Badge model."""

    def test_create_badge(self, test_app, test_user):
        """Badge should be created and linked to user."""
        with test_app.app_context():
            badge = Badge(
                user_id=test_user.id,
                badge_type="first_entry",
            )
            db.session.add(badge)
            db.session.commit()

            fetched = Badge.query.first()
            assert fetched.badge_type == "first_entry"
            assert fetched.earned_at is not None

    def test_badge_info_property(self, test_app, test_user):
        """Badge info should return correct metadata."""
        with test_app.app_context():
            badge = Badge(user_id=test_user.id, badge_type="first_entry")
            info = badge.info
            assert info["name"] == "First Step"
            assert info["icon"] == "🌱"

    def test_badge_uniqueness(self, test_app, test_user):
        """Same badge type for same user should violate constraint."""
        with test_app.app_context():
            badge1 = Badge(user_id=test_user.id, badge_type="first_entry")
            db.session.add(badge1)
            db.session.commit()

            badge2 = Badge(user_id=test_user.id, badge_type="first_entry")
            db.session.add(badge2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_unknown_badge_type(self, test_app, test_user):
        """Unknown badge type should return default info."""
        with test_app.app_context():
            badge = Badge(user_id=test_user.id, badge_type="unknown_type")
            info = badge.info
            assert info["name"] == "unknown_type"
            assert info["icon"] == "🏅"
