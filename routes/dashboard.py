"""
Dashboard routes: overview, history, and data visualizations.
"""

from datetime import date, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import CarbonEntry, db
from utils.emission_factors import INDIA_DAILY_AVERAGE
from utils.tips_engine import get_personalized_tips, get_comparison_insight
from utils.badges import get_badge_progress

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard with today's summary, weekly trend, and badges."""
    today = date.today()

    # Today's entry (if exists)
    todays_entry = CarbonEntry.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    # Last 7 days entries for the sparkline
    week_ago = today - timedelta(days=6)
    recent_entries = (
        CarbonEntry.query.filter(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.date >= week_ago,
            CarbonEntry.date <= today,
        )
        .order_by(CarbonEntry.date.asc())
        .all()
    )

    # Stats
    total_entries = current_user.entries.count()
    if total_entries > 0:
        avg_co2 = (
            db.session.query(db.func.avg(CarbonEntry.total_co2))
            .filter(CarbonEntry.user_id == current_user.id)
            .scalar() or 0.0
        )
    else:
        avg_co2 = 0.0

    # Comparison insight
    comparison = None
    tips = []
    if todays_entry:
        comparison = get_comparison_insight(todays_entry.total_co2)
        tips = get_personalized_tips(todays_entry.category_breakdown, max_tips=3)

    # Badge progress
    badge_progress = get_badge_progress(current_user)

    return render_template(
        "dashboard/dashboard.html",
        todays_entry=todays_entry,
        recent_entries=recent_entries,
        total_entries=total_entries,
        avg_co2=round(avg_co2, 2),
        comparison=comparison,
        tips=tips,
        badge_progress=badge_progress,
        india_average=INDIA_DAILY_AVERAGE,
    )


@dashboard_bp.route("/history")
@login_required
def history():
    """Paginated history of all carbon footprint entries."""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    entries = (
        CarbonEntry.query.filter_by(user_id=current_user.id)
        .order_by(CarbonEntry.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "dashboard/history.html",
        entries=entries,
        india_average=INDIA_DAILY_AVERAGE,
    )
