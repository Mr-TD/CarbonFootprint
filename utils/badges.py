"""
Gamification badge system.

Awards badges based on user milestones and behaviour patterns.
"""

from datetime import timedelta, date
from models import Badge, CarbonEntry, db


def check_and_award_badges(user):
    """
    Check if a user qualifies for any new badges and award them.

    Args:
        user: User model instance

    Returns:
        list of newly awarded Badge instances
    """
    newly_awarded = []
    existing = {b.badge_type for b in user.badges.all()}

    # 1. First Entry badge
    if "first_entry" not in existing:
        entry_count = user.entries.count()
        if entry_count >= 1:
            badge = _award_badge(user, "first_entry")
            newly_awarded.append(badge)

    # 2. Week Streak badge (7 consecutive days)
    if "week_streak" not in existing:
        if _has_consecutive_days(user, 7):
            badge = _award_badge(user, "week_streak")
            newly_awarded.append(badge)

    # 3. Low Carbon Day (any day under 5 kg CO₂e)
    if "low_carbon_day" not in existing:
        low_carbon = user.entries.filter(CarbonEntry.total_co2 < 5.0).first()
        if low_carbon:
            badge = _award_badge(user, "low_carbon_day")
            newly_awarded.append(badge)

    # 4. Green Commuter (7 entries with transport <= 1 kg CO₂e)
    if "green_commuter" not in existing:
        green_transport_count = user.entries.filter(
            CarbonEntry.transport_co2 <= 1.0
        ).count()
        if green_transport_count >= 7:
            badge = _award_badge(user, "green_commuter")
            newly_awarded.append(badge)

    # 5. Eco Warrior (30 entries below India average of 5.2 kg)
    if "eco_warrior" not in existing:
        below_average_count = user.entries.filter(
            CarbonEntry.total_co2 < 5.2
        ).count()
        if below_average_count >= 30:
            badge = _award_badge(user, "eco_warrior")
            newly_awarded.append(badge)

    return newly_awarded


def _award_badge(user, badge_type):
    """Create and persist a new badge for the user."""
    badge = Badge(user_id=user.id, badge_type=badge_type)
    db.session.add(badge)
    db.session.commit()
    return badge


def _has_consecutive_days(user, required_days):
    """
    Check if user has entries for N consecutive days ending today.

    Args:
        user: User model instance
        required_days: Number of consecutive days required

    Returns:
        bool: True if user has the required streak
    """
    today = date.today()
    dates_with_entries = set()

    entries = user.entries.filter(
        CarbonEntry.date >= today - timedelta(days=required_days + 7)
    ).all()

    for entry in entries:
        dates_with_entries.add(entry.date)

    # Check for any streak of required_days length
    for start_offset in range(required_days + 7):
        start_date = today - timedelta(days=start_offset)
        streak = True
        for day in range(required_days):
            check_date = start_date - timedelta(days=day)
            if check_date not in dates_with_entries:
                streak = False
                break
        if streak:
            return True

    return False


def get_badge_progress(user):
    """
    Get progress toward each badge for the user.

    Args:
        user: User model instance

    Returns:
        list of dicts with badge info and progress
    """
    existing = {b.badge_type for b in user.badges.all()}
    progress = []

    # First Entry
    entry_count = user.entries.count()
    progress.append({
        "badge_type": "first_entry",
        "earned": "first_entry" in existing,
        "current": min(entry_count, 1),
        "target": 1,
        "percentage": 100 if entry_count >= 1 else 0,
    })

    # Week Streak
    progress.append({
        "badge_type": "week_streak",
        "earned": "week_streak" in existing,
        "current": min(_get_current_streak(user), 7),
        "target": 7,
        "percentage": min(100, int((_get_current_streak(user) / 7) * 100)),
    })

    # Low Carbon Day
    low_carbon_count = user.entries.filter(CarbonEntry.total_co2 < 5.0).count()
    progress.append({
        "badge_type": "low_carbon_day",
        "earned": "low_carbon_day" in existing,
        "current": min(low_carbon_count, 1),
        "target": 1,
        "percentage": 100 if low_carbon_count >= 1 else 0,
    })

    # Green Commuter
    green_count = user.entries.filter(CarbonEntry.transport_co2 <= 1.0).count()
    progress.append({
        "badge_type": "green_commuter",
        "earned": "green_commuter" in existing,
        "current": min(green_count, 7),
        "target": 7,
        "percentage": min(100, int((green_count / 7) * 100)),
    })

    # Eco Warrior
    below_avg = user.entries.filter(CarbonEntry.total_co2 < 5.2).count()
    progress.append({
        "badge_type": "eco_warrior",
        "earned": "eco_warrior" in existing,
        "current": min(below_avg, 30),
        "target": 30,
        "percentage": min(100, int((below_avg / 30) * 100)),
    })

    # Attach badge metadata
    for item in progress:
        item["info"] = Badge.BADGE_INFO.get(item["badge_type"], {})

    return progress


def _get_current_streak(user):
    """Get the current consecutive-day streak for the user."""
    today = date.today()
    streak = 0
    for i in range(60):  # Check up to 60 days back
        check_date = today - timedelta(days=i)
        has_entry = user.entries.filter(CarbonEntry.date == check_date).first()
        if has_entry:
            streak += 1
        else:
            break
    return streak
