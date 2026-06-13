"""
India-specific carbon emission factors.

Sources:
    - Central Electricity Authority (CEA) CO2 Baseline Database v20.0, 2024
    - IPCC Emission Factor Database
    - Indian Railways sustainability reports
    - ICAO Carbon Emissions Calculator methodology
    - Energy Alternatives India (EAI) dietary studies
    - NITI Aayog waste sector reports

All values are in kg CO₂e (carbon dioxide equivalent).
"""

# ===========================================================================
# TRANSPORT EMISSION FACTORS (kg CO₂e per km or per litre)
# ===========================================================================

TRANSPORT_FUEL = {
    # Per litre of fuel consumed
    "petrol": 2.31,       # IPCC default for motor gasoline
    "diesel": 2.68,       # IPCC default for gas/diesel oil
    "cng": 1.63,          # Compressed Natural Gas
    "electric": 0.0,      # Zero tailpipe; grid emissions in energy category
}

TRANSPORT_MODE = {
    # Per passenger-km
    "car_petrol": 0.192,     # Average Indian car (~12 km/L petrol)
    "car_diesel": 0.171,     # Average Indian car (~15 km/L diesel)
    "car_cng": 0.130,        # CNG car (~12.5 km/kg)
    "car_electric": 0.050,   # EV (~0.15 kWh/km × grid factor)
    "two_wheeler": 0.052,    # Average scooter/motorbike (~45 km/L)
    "auto_rickshaw": 0.150,  # Shared auto-rickshaw
    "bus": 0.089,            # Public bus (per passenger-km)
    "metro": 0.035,          # Metro rail
    "train": 0.041,          # Indian Railways (per passenger-km)
    "bicycle": 0.0,          # Zero emissions
    "walking": 0.0,          # Zero emissions
    "flight_domestic": 0.255,    # Domestic flight (per passenger-km)
    "flight_international": 0.195,  # International flight (per passenger-km)
}

# Average fuel efficiency for estimating fuel from distance (km/litre)
VEHICLE_EFFICIENCY = {
    "car_petrol": 12.0,
    "car_diesel": 15.0,
    "car_cng": 12.5,
    "two_wheeler": 45.0,
}

# ===========================================================================
# ENERGY EMISSION FACTORS
# ===========================================================================

# Indian national grid average (CEA 2024, Version 20.0)
ELECTRICITY_GRID_FACTOR = 0.716  # kg CO₂ per kWh

# LPG cylinder (standard 14.2 kg domestic cylinder)
LPG_CYLINDER_CO2 = 42.5  # kg CO₂e per cylinder (14.2 kg × 2.99 kg CO₂/kg LPG)

# Natural gas (piped) per cubic metre
PIPED_GAS_CO2 = 2.0  # kg CO₂e per m³

# Solar panel offset: assumes 4 kWh/day average generation in India
SOLAR_DAILY_OFFSET = 4.0 * ELECTRICITY_GRID_FACTOR  # kg CO₂e saved per day

# ===========================================================================
# FOOD / DIET EMISSION FACTORS (kg CO₂e per meal)
# ===========================================================================

FOOD_PER_MEAL = {
    "vegan": 0.45,             # Plant-based only
    "vegetarian": 0.72,        # Indian vegetarian (includes dairy)
    "non_vegetarian": 1.53,    # Includes meat/poultry
    "heavy_non_veg": 2.38,     # Red meat heavy meals
}

# ===========================================================================
# WASTE EMISSION FACTORS (kg CO₂e)
# ===========================================================================

# Per kg of mixed waste sent to landfill
WASTE_LANDFILL_FACTOR = 0.58  # kg CO₂e per kg waste (NITI Aayog)

# Recycling reduces waste emissions by this fraction
RECYCLING_REDUCTION = 0.70  # 70% reduction when recycled vs landfill

# Composting organic waste
COMPOST_REDUCTION = 0.85  # 85% reduction when composted

# ===========================================================================
# WATER EMISSION FACTORS
# ===========================================================================

# Per litre of treated water supply (pumping + treatment)
WATER_FACTOR = 0.0003  # kg CO₂e per litre

# Average daily water usage in Indian households (litres per person)
AVERAGE_DAILY_WATER = 135  # litres (Central Ground Water Board)

# ===========================================================================
# REFERENCE VALUES
# ===========================================================================

# India average annual per capita CO₂ emissions: ~1.9 tonnes
# Daily average: ~5.2 kg CO₂e per person per day
INDIA_DAILY_AVERAGE = 5.2  # kg CO₂e

# Global average annual per capita: ~4.7 tonnes
# Daily average: ~12.9 kg CO₂e per person per day
GLOBAL_DAILY_AVERAGE = 12.9  # kg CO₂e

# Target for climate goals (well below 2°C): ~2 tonnes/year
# Daily target: ~5.5 kg CO₂e per person per day
CLIMATE_TARGET_DAILY = 5.5  # kg CO₂e
