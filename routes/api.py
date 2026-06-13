"""
JSON API endpoints for chart data.

Used by Chart.js on the frontend to render dynamic visualizations.
All endpoints require authentication.
"""

from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from models import CarbonEntry
from utils.emission_factors import INDIA_DAILY_AVERAGE

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/chart-data")
@login_required
def chart_data():
    """
    Return daily carbon footprint data for Chart.js line chart.

    Query params:
        days: Number of days to look back (default: 7, max: 90)

    Returns:
        JSON with labels (dates), data (totals), and category breakdown
    """
    days = request.args.get("days", 7, type=int)
    days = min(max(days, 1), 90)  # Clamp to 1-90

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    entries = (
        CarbonEntry.query.filter(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.date >= start_date,
            CarbonEntry.date <= today,
        )
        .order_by(CarbonEntry.date.asc())
        .all()
    )

    # Build a map of date -> entry for gap filling
    entry_map = {e.date: e for e in entries}

    labels = []
    totals = []
    transport = []
    energy = []
    food = []
    waste = []
    water = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        labels.append(d.strftime("%d %b"))

        entry = entry_map.get(d)
        if entry:
            totals.append(round(entry.total_co2, 2))
            transport.append(round(entry.transport_co2, 2))
            energy.append(round(entry.energy_co2, 2))
            food.append(round(entry.food_co2, 2))
            waste.append(round(entry.waste_co2, 2))
            water.append(round(entry.water_co2, 2))
        else:
            totals.append(None)
            transport.append(None)
            energy.append(None)
            food.append(None)
            waste.append(None)
            water.append(None)

    return jsonify({
        "labels": labels,
        "datasets": {
            "total": totals,
            "transport": transport,
            "energy": energy,
            "food": food,
            "waste": waste,
            "water": water,
        },
        "india_average": INDIA_DAILY_AVERAGE,
    })


@api_bp.route("/category-breakdown/<int:entry_id>")
@login_required
def category_breakdown(entry_id):
    """
    Return category breakdown for a specific entry (doughnut chart).

    Returns:
        JSON with labels and values for each category
    """
    entry = CarbonEntry.query.filter_by(
        id=entry_id, user_id=current_user.id
    ).first()

    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    breakdown = entry.category_breakdown

    return jsonify({
        "labels": ["Transport", "Energy", "Food", "Waste", "Water"],
        "values": [
            breakdown["transport"],
            breakdown["energy"],
            breakdown["food"],
            breakdown["waste"],
            breakdown["water"],
        ],
        "total": round(entry.total_co2, 2),
    })
