"""
Core carbon footprint calculation engine.

All functions are pure (no side effects) for easy testing.
Each function takes user input and returns CO₂e in kg.
"""

from utils.emission_factors import (
    TRANSPORT_MODE,
    ELECTRICITY_GRID_FACTOR,
    LPG_CYLINDER_CO2,
    SOLAR_DAILY_OFFSET,
    FOOD_PER_MEAL,
    WASTE_LANDFILL_FACTOR,
    RECYCLING_REDUCTION,
    WATER_FACTOR,
)


def calculate_transport(mode, distance_km):
    """
    Calculate transport emissions.

    Args:
        mode: Transport mode key from TRANSPORT_MODE dict
        distance_km: Distance travelled in kilometres (must be >= 0)

    Returns:
        float: CO₂e emissions in kg

    Raises:
        ValueError: If distance is negative or mode is unknown
    """
    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    factor = TRANSPORT_MODE.get(mode)
    if factor is None:
        raise ValueError(f"Unknown transport mode: {mode}")

    return round(factor * distance_km, 3)


def calculate_energy(electricity_kwh, lpg_cylinders=0, has_solar=False):
    """
    Calculate home energy emissions.

    Args:
        electricity_kwh: Daily electricity consumption in kWh (must be >= 0)
        lpg_cylinders: Monthly LPG cylinders used (0-5, will be divided by 30 for daily)
        has_solar: Whether the household has solar panels

    Returns:
        float: CO₂e emissions in kg

    Raises:
        ValueError: If inputs are negative
    """
    if electricity_kwh < 0:
        raise ValueError("Electricity consumption cannot be negative")
    if lpg_cylinders < 0:
        raise ValueError("LPG cylinders cannot be negative")

    # Electricity emissions
    electricity_co2 = electricity_kwh * ELECTRICITY_GRID_FACTOR

    # LPG emissions (convert monthly to daily)
    lpg_daily_co2 = (lpg_cylinders * LPG_CYLINDER_CO2) / 30.0

    # Solar offset (only reduces electricity emissions)
    solar_offset = SOLAR_DAILY_OFFSET if has_solar else 0.0

    total = electricity_co2 + lpg_daily_co2 - solar_offset
    return round(max(total, 0.0), 3)  # Cannot be negative


def calculate_food(diet_type, num_meals):
    """
    Calculate food-related emissions.

    Args:
        diet_type: Diet type key from FOOD_PER_MEAL dict
        num_meals: Number of meals consumed (0-10)

    Returns:
        float: CO₂e emissions in kg

    Raises:
        ValueError: If num_meals is negative or diet_type is unknown
    """
    if num_meals < 0:
        raise ValueError("Number of meals cannot be negative")

    factor = FOOD_PER_MEAL.get(diet_type)
    if factor is None:
        raise ValueError(f"Unknown diet type: {diet_type}")

    return round(factor * num_meals, 3)


def calculate_waste(waste_kg, recycling_percentage=0):
    """
    Calculate waste disposal emissions.

    Args:
        waste_kg: Waste generated in kg (must be >= 0)
        recycling_percentage: Percentage of waste recycled (0-100)

    Returns:
        float: CO₂e emissions in kg

    Raises:
        ValueError: If waste_kg is negative or recycling_percentage out of range
    """
    if waste_kg < 0:
        raise ValueError("Waste amount cannot be negative")
    if not 0 <= recycling_percentage <= 100:
        raise ValueError("Recycling percentage must be between 0 and 100")

    recycled_fraction = recycling_percentage / 100.0
    landfill_fraction = 1.0 - recycled_fraction

    # Landfill waste at full factor
    landfill_co2 = waste_kg * landfill_fraction * WASTE_LANDFILL_FACTOR

    # Recycled waste at reduced factor
    recycled_co2 = (
        waste_kg * recycled_fraction * WASTE_LANDFILL_FACTOR * (1 - RECYCLING_REDUCTION)
    )

    return round(landfill_co2 + recycled_co2, 3)


def calculate_water(litres_used):
    """
    Calculate water usage emissions.

    Args:
        litres_used: Daily water consumption in litres (must be >= 0)

    Returns:
        float: CO₂e emissions in kg

    Raises:
        ValueError: If litres is negative
    """
    if litres_used < 0:
        raise ValueError("Water usage cannot be negative")

    return round(litres_used * WATER_FACTOR, 3)


def calculate_total(transport_co2, energy_co2, food_co2, waste_co2, water_co2):
    """
    Aggregate total daily carbon footprint.

    Args:
        transport_co2: Transport emissions in kg CO₂e
        energy_co2: Energy emissions in kg CO₂e
        food_co2: Food emissions in kg CO₂e
        waste_co2: Waste emissions in kg CO₂e
        water_co2: Water emissions in kg CO₂e

    Returns:
        dict: Contains individual categories and total
    """
    total = transport_co2 + energy_co2 + food_co2 + waste_co2 + water_co2

    return {
        "transport": round(transport_co2, 2),
        "energy": round(energy_co2, 2),
        "food": round(food_co2, 2),
        "waste": round(waste_co2, 2),
        "water": round(water_co2, 2),
        "total": round(total, 2),
    }
