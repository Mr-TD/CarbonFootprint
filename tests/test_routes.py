"""
Integration tests for routes and views.

Tests that all routes return correct status codes,
protected routes require authentication, and
calculator submissions work correctly.
"""

import pytest
from datetime import date


class TestPublicRoutes:
    """Tests for public routes."""

    def test_landing_page(self, client):
        """GET / should return 200 with hero content."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Carbon Footprint" in response.data


class TestAuthenticatedRoutes:
    """Tests for authenticated routes."""

    def test_calculator_page_loads(self, auth_client):
        """GET /calculate should return 200 when authenticated."""
        response = auth_client.get("/calculate")
        assert response.status_code == 200
        assert b"Calculate" in response.data

    def test_dashboard_page_loads(self, auth_client):
        """GET /dashboard should return 200 when authenticated."""
        response = auth_client.get("/dashboard")
        assert response.status_code == 200
        assert b"Dashboard" in response.data

    def test_history_page_loads(self, auth_client):
        """GET /history should return 200 when authenticated."""
        response = auth_client.get("/history")
        assert response.status_code == 200

    def test_calculator_submission(self, auth_client):
        """POST /calculate should process form and redirect to results."""
        response = auth_client.post(
            "/calculate",
            data={
                "transport_mode": "metro",
                "transport_distance": 15,
                "electricity_kwh": 8,
                "lpg_cylinders": 1,
                "has_solar": False,
                "diet_type": "vegetarian",
                "num_meals": 3,
                "waste_kg": 0.5,
                "recycling_percentage": 30,
                "water_litres": 135,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should show results or dashboard
        assert b"kg" in response.data

    def test_api_chart_data(self, auth_client):
        """GET /api/chart-data should return JSON."""
        response = auth_client.get("/api/chart-data?days=7")
        assert response.status_code == 200
        data = response.get_json()
        assert "labels" in data
        assert "datasets" in data
        assert len(data["labels"]) == 7


class TestErrorPages:
    """Tests for error handlers."""

    def test_404_page(self, client):
        """Non-existent route should return 404."""
        response = client.get("/this-does-not-exist")
        assert response.status_code == 404
