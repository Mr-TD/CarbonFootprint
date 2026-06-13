"""
Calculator routes: multi-step carbon footprint calculator.

Processes form input, calculates emissions using the engine,
saves entries, and displays results with personalized tips.
"""

from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models import CarbonEntry, db
from forms import CarbonCalculatorForm
from utils.calculator_engine import (
    calculate_transport,
    calculate_energy,
    calculate_food,
    calculate_waste,
    calculate_water,
    calculate_total,
)
from utils.tips_engine import get_personalized_tips, get_comparison_insight
from utils.badges import check_and_award_badges

calculator_bp = Blueprint("calculator", __name__)


@calculator_bp.route("/calculate", methods=["GET", "POST"])
@login_required
def calculate():
    """Render calculator form and process submissions."""
    form = CarbonCalculatorForm()

    if form.validate_on_submit():
        # Calculate each category
        transport_co2 = calculate_transport(
            mode=form.transport_mode.data,
            distance_km=form.transport_distance.data,
        )
        energy_co2 = calculate_energy(
            electricity_kwh=form.electricity_kwh.data,
            lpg_cylinders=form.lpg_cylinders.data or 0,
            has_solar=form.has_solar.data,
        )
        food_co2 = calculate_food(
            diet_type=form.diet_type.data,
            num_meals=form.num_meals.data,
        )
        waste_co2 = calculate_waste(
            waste_kg=form.waste_kg.data,
            recycling_percentage=form.recycling_percentage.data or 0,
        )
        water_co2 = calculate_water(
            litres_used=form.water_litres.data,
        )

        # Get totals
        result = calculate_total(
            transport_co2, energy_co2, food_co2, waste_co2, water_co2
        )

        # Store raw input details for drill-down
        details = {
            "transport_mode": form.transport_mode.data,
            "transport_distance": form.transport_distance.data,
            "electricity_kwh": form.electricity_kwh.data,
            "lpg_cylinders": form.lpg_cylinders.data or 0,
            "has_solar": form.has_solar.data,
            "diet_type": form.diet_type.data,
            "num_meals": form.num_meals.data,
            "waste_kg": form.waste_kg.data,
            "recycling_percentage": form.recycling_percentage.data or 0,
            "water_litres": form.water_litres.data,
        }

        # Check if entry already exists for today (update instead of duplicate)
        today = date.today()
        existing_entry = CarbonEntry.query.filter_by(
            user_id=current_user.id, date=today
        ).first()

        if existing_entry:
            # Update existing entry
            existing_entry.transport_co2 = result["transport"]
            existing_entry.energy_co2 = result["energy"]
            existing_entry.food_co2 = result["food"]
            existing_entry.waste_co2 = result["waste"]
            existing_entry.water_co2 = result["water"]
            existing_entry.total_co2 = result["total"]
            existing_entry.set_details(details)
            entry = existing_entry
            flash("Today's entry has been updated!", "success")
        else:
            # Create new entry
            entry = CarbonEntry(
                user_id=current_user.id,
                date=today,
                transport_co2=result["transport"],
                energy_co2=result["energy"],
                food_co2=result["food"],
                waste_co2=result["waste"],
                water_co2=result["water"],
                total_co2=result["total"],
            )
            entry.set_details(details)
            db.session.add(entry)
            flash("Your carbon footprint has been calculated!", "success")

        db.session.commit()

        # Check for new badges
        new_badges = check_and_award_badges(current_user)
        for badge in new_badges:
            flash(
                f"🏆 New badge earned: {badge.info['icon']} {badge.info['name']}!",
                "badge",
            )

        return redirect(url_for("calculator.results", entry_id=entry.id))

    return render_template("calculator/calculate.html", form=form)


@calculator_bp.route("/results/<int:entry_id>")
@login_required
def results(entry_id):
    """Display detailed results for a carbon footprint entry."""
    entry = CarbonEntry.query.filter_by(
        id=entry_id, user_id=current_user.id
    ).first_or_404()

    # Generate personalized tips
    tips = get_personalized_tips(entry.category_breakdown)

    # Get comparison insight
    comparison = get_comparison_insight(entry.total_co2)

    return render_template(
        "calculator/calculate.html",
        entry=entry,
        tips=tips,
        comparison=comparison,
        show_results=True,
        form=CarbonCalculatorForm(),
    )
