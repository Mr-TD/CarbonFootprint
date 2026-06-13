"""
Flask-WTF forms with validation for CarbonCredit.

All forms include CSRF protection via CSRFProtect.
Validators ensure data integrity before processing.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    FloatField,
    IntegerField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    ValidationError,
    Optional,
)
# None of the auth forms are needed since authentication pages have been removed.


class CarbonCalculatorForm(FlaskForm):
    """
    Multi-category carbon footprint calculator form.

    Categories: Transport, Energy, Food, Waste, Water
    """

    # --- TRANSPORT ---
    transport_mode = SelectField(
        "Primary Transport Mode",
        choices=[
            ("", "-- Select mode --"),
            ("car_petrol", "Car (Petrol)"),
            ("car_diesel", "Car (Diesel)"),
            ("car_cng", "Car (CNG)"),
            ("car_electric", "Car (Electric)"),
            ("two_wheeler", "Two Wheeler (Scooter/Bike)"),
            ("auto_rickshaw", "Auto Rickshaw"),
            ("bus", "Bus"),
            ("metro", "Metro"),
            ("train", "Train"),
            ("bicycle", "Bicycle"),
            ("walking", "Walking"),
            ("flight_domestic", "Flight (Domestic)"),
            ("flight_international", "Flight (International)"),
        ],
        validators=[DataRequired(message="Please select a transport mode")],
    )
    transport_distance = FloatField(
        "Distance Travelled (km)",
        validators=[
            DataRequired(message="Please enter distance"),
            NumberRange(min=0, max=15000, message="Distance must be 0-15,000 km"),
        ],
        render_kw={"placeholder": "e.g., 25", "min": "0", "step": "0.1"},
    )

    # --- ENERGY ---
    electricity_kwh = FloatField(
        "Daily Electricity Usage (kWh)",
        validators=[
            DataRequired(message="Please enter electricity usage"),
            NumberRange(min=0, max=500, message="Must be 0-500 kWh"),
        ],
        render_kw={"placeholder": "e.g., 8", "min": "0", "step": "0.1"},
    )
    lpg_cylinders = IntegerField(
        "Monthly LPG Cylinders",
        validators=[
            Optional(),
            NumberRange(min=0, max=5, message="Must be 0-5 cylinders"),
        ],
        default=1,
        render_kw={"placeholder": "e.g., 1", "min": "0", "max": "5"},
    )
    has_solar = BooleanField("I have rooftop solar panels")

    # --- FOOD ---
    diet_type = SelectField(
        "Diet Type",
        choices=[
            ("vegetarian", "Vegetarian"),
            ("vegan", "Vegan"),
            ("non_vegetarian", "Non-Vegetarian"),
            ("heavy_non_veg", "Heavy Non-Veg (Red Meat)"),
        ],
        validators=[DataRequired(message="Please select your diet type")],
    )
    num_meals = IntegerField(
        "Number of Meals Today",
        validators=[
            DataRequired(message="Please enter number of meals"),
            NumberRange(min=0, max=10, message="Must be 0-10 meals"),
        ],
        default=3,
        render_kw={"placeholder": "e.g., 3", "min": "0", "max": "10"},
    )

    # --- WASTE ---
    waste_kg = FloatField(
        "Waste Generated (kg)",
        validators=[
            DataRequired(message="Please enter waste amount"),
            NumberRange(min=0, max=50, message="Must be 0-50 kg"),
        ],
        render_kw={"placeholder": "e.g., 0.5", "min": "0", "step": "0.1"},
    )
    recycling_percentage = IntegerField(
        "Recycling Percentage",
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="Must be between 0 and 100"),
        ],
        default=20,
        render_kw={"placeholder": "e.g., 30", "min": "0", "max": "100"},
    )

    # --- WATER ---
    water_litres = FloatField(
        "Water Used (litres)",
        validators=[
            DataRequired(message="Please enter water usage"),
            NumberRange(min=0, max=5000, message="Must be 0-5,000 litres"),
        ],
        render_kw={"placeholder": "e.g., 135", "min": "0", "step": "1"},
    )

    submit = SubmitField("Calculate My Footprint")
