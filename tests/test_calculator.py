"""
Unit tests for the carbon calculator engine.

Tests all five calculation functions with normal inputs,
edge cases, and error conditions.
"""

import pytest
from utils.calculator_engine import (
    calculate_transport,
    calculate_energy,
    calculate_food,
    calculate_waste,
    calculate_water,
    calculate_total,
)


class TestCalculateTransport:
    """Tests for calculate_transport()."""

    def test_car_petrol_normal(self):
        """Normal car petrol commute: 25 km."""
        result = calculate_transport("car_petrol", 25)
        assert result == pytest.approx(0.192 * 25, abs=0.01)

    def test_metro_commute(self):
        """Metro commute: 15 km."""
        result = calculate_transport("metro", 15)
        assert result == pytest.approx(0.035 * 15, abs=0.01)

    def test_bicycle_zero_emissions(self):
        """Bicycle should produce zero emissions."""
        result = calculate_transport("bicycle", 50)
        assert result == 0.0

    def test_walking_zero_emissions(self):
        """Walking should produce zero emissions."""
        result = calculate_transport("walking", 10)
        assert result == 0.0

    def test_zero_distance(self):
        """Zero distance should produce zero emissions."""
        result = calculate_transport("car_petrol", 0)
        assert result == 0.0

    def test_negative_distance_raises(self):
        """Negative distance should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_transport("car_petrol", -5)

    def test_unknown_mode_raises(self):
        """Unknown transport mode should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown transport mode"):
            calculate_transport("helicopter", 10)

    def test_flight_domestic(self):
        """Domestic flight: 1000 km."""
        result = calculate_transport("flight_domestic", 1000)
        assert result == pytest.approx(255.0, abs=0.1)

    def test_two_wheeler(self):
        """Two-wheeler commute: 30 km."""
        result = calculate_transport("two_wheeler", 30)
        assert result == pytest.approx(0.052 * 30, abs=0.01)


class TestCalculateEnergy:
    """Tests for calculate_energy()."""

    def test_electricity_only(self):
        """Just electricity: 8 kWh."""
        result = calculate_energy(8, 0, False)
        assert result == pytest.approx(8 * 0.716, abs=0.01)

    def test_with_lpg(self):
        """Electricity + 1 LPG cylinder per month."""
        result = calculate_energy(5, 1, False)
        expected = (5 * 0.716) + (1 * 42.5 / 30.0)
        assert result == pytest.approx(expected, abs=0.01)

    def test_with_solar_offset(self):
        """Solar panels should offset emissions."""
        result_without = calculate_energy(10, 0, False)
        result_with = calculate_energy(10, 0, True)
        assert result_with < result_without

    def test_solar_doesnt_go_negative(self):
        """Solar offset shouldn't make emissions negative."""
        result = calculate_energy(1, 0, True)
        assert result >= 0.0

    def test_zero_usage(self):
        """Zero electricity and LPG."""
        result = calculate_energy(0, 0, False)
        assert result == 0.0

    def test_negative_kwh_raises(self):
        """Negative kWh should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_energy(-5, 0, False)

    def test_negative_lpg_raises(self):
        """Negative LPG should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_energy(5, -1, False)


class TestCalculateFood:
    """Tests for calculate_food()."""

    def test_vegetarian_three_meals(self):
        """Three vegetarian meals."""
        result = calculate_food("vegetarian", 3)
        assert result == pytest.approx(0.72 * 3, abs=0.01)

    def test_vegan_meal(self):
        """One vegan meal."""
        result = calculate_food("vegan", 1)
        assert result == pytest.approx(0.45, abs=0.01)

    def test_non_veg_higher_than_veg(self):
        """Non-veg should produce more emissions than veg."""
        veg = calculate_food("vegetarian", 1)
        non_veg = calculate_food("non_vegetarian", 1)
        assert non_veg > veg

    def test_zero_meals(self):
        """Zero meals should produce zero emissions."""
        result = calculate_food("vegetarian", 0)
        assert result == 0.0

    def test_negative_meals_raises(self):
        """Negative meals should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_food("vegetarian", -1)

    def test_unknown_diet_raises(self):
        """Unknown diet type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown diet type"):
            calculate_food("carnivore", 3)


class TestCalculateWaste:
    """Tests for calculate_waste()."""

    def test_no_recycling(self):
        """1 kg waste, no recycling."""
        result = calculate_waste(1.0, 0)
        assert result == pytest.approx(0.58, abs=0.01)

    def test_full_recycling(self):
        """1 kg waste, 100% recycling — much lower emissions."""
        result = calculate_waste(1.0, 100)
        no_recycle = calculate_waste(1.0, 0)
        assert result < no_recycle

    def test_partial_recycling(self):
        """1 kg waste, 50% recycling."""
        result = calculate_waste(1.0, 50)
        assert result > 0
        assert result < calculate_waste(1.0, 0)

    def test_zero_waste(self):
        """Zero waste should produce zero emissions."""
        result = calculate_waste(0, 0)
        assert result == 0.0

    def test_negative_waste_raises(self):
        """Negative waste should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_waste(-1, 0)

    def test_invalid_recycling_raises(self):
        """Recycling percentage out of range should raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            calculate_waste(1, 150)


class TestCalculateWater:
    """Tests for calculate_water()."""

    def test_average_usage(self):
        """Average Indian water usage: 135 litres."""
        result = calculate_water(135)
        assert result == pytest.approx(135 * 0.0003, abs=0.001)

    def test_zero_water(self):
        """Zero water usage."""
        result = calculate_water(0)
        assert result == 0.0

    def test_negative_water_raises(self):
        """Negative water should raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_water(-10)


class TestCalculateTotal:
    """Tests for calculate_total()."""

    def test_aggregation(self):
        """Total should be sum of all categories."""
        result = calculate_total(1.0, 2.0, 3.0, 0.5, 0.1)
        assert result["total"] == pytest.approx(6.6, abs=0.01)

    def test_all_zeros(self):
        """All zero inputs should produce zero total."""
        result = calculate_total(0, 0, 0, 0, 0)
        assert result["total"] == 0.0

    def test_result_structure(self):
        """Result should contain all expected keys."""
        result = calculate_total(1, 2, 3, 4, 5)
        assert "transport" in result
        assert "energy" in result
        assert "food" in result
        assert "waste" in result
        assert "water" in result
        assert "total" in result

    def test_rounding(self):
        """Values should be rounded to 2 decimal places."""
        result = calculate_total(1.234, 2.567, 3.891, 0.123, 0.456)
        assert result["transport"] == 1.23
        assert result["energy"] == 2.57
        assert result["total"] == round(1.234 + 2.567 + 3.891 + 0.123 + 0.456, 2)
