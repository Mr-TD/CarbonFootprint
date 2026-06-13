"""
Personalized carbon reduction tips engine.

Analyzes a user's carbon footprint entry and returns
actionable, India-specific tips ranked by potential impact.
"""

from utils.emission_factors import INDIA_DAILY_AVERAGE


# Tip database organized by category
TIPS_DATABASE = {
    "transport": [
        {
            "tip": "Switch to metro or local train for your daily commute",
            "potential_saving": "Up to 60% reduction in transport emissions",
            "icon": "🚇",
            "priority": 1,
        },
        {
            "tip": "Carpool with colleagues — sharing a ride with 3 people cuts emissions by 75%",
            "potential_saving": "~3-5 kg CO₂e saved per day",
            "icon": "🚗",
            "priority": 2,
        },
        {
            "tip": "Consider an electric two-wheeler — India offers FAME II subsidies up to ₹15,000",
            "potential_saving": "~70% lower than petrol two-wheelers",
            "icon": "⚡",
            "priority": 3,
        },
        {
            "tip": "For short distances (< 3 km), walk or cycle instead of driving",
            "potential_saving": "Eliminates 0.5-1 kg CO₂e per trip",
            "icon": "🚲",
            "priority": 4,
        },
        {
            "tip": "Avoid unnecessary flights — one domestic flight ≈ 2 weeks of driving",
            "potential_saving": "~150-250 kg CO₂e per avoided flight",
            "icon": "✈️",
            "priority": 5,
        },
    ],
    "energy": [
        {
            "tip": "Switch to LED bulbs — they use 75% less energy than incandescent bulbs",
            "potential_saving": "~0.5 kg CO₂e per day for a typical home",
            "icon": "💡",
            "priority": 1,
        },
        {
            "tip": "Install rooftop solar — India's PM Surya Ghar scheme provides subsidies up to ₹78,000",
            "potential_saving": "2-4 kg CO₂e offset per day",
            "icon": "☀️",
            "priority": 2,
        },
        {
            "tip": "Set AC to 24°C instead of 18°C — each degree saves ~6% energy",
            "potential_saving": "~1-2 kg CO₂e per day in summer",
            "icon": "❄️",
            "priority": 3,
        },
        {
            "tip": "Use a 5-star rated refrigerator and washing machine",
            "potential_saving": "~30-40% energy savings vs unrated appliances",
            "icon": "⭐",
            "priority": 4,
        },
        {
            "tip": "Unplug chargers and devices when not in use — phantom loads add up",
            "potential_saving": "~0.2-0.5 kg CO₂e per day",
            "icon": "🔌",
            "priority": 5,
        },
    ],
    "food": [
        {
            "tip": "Eat one more vegetarian meal per day — Indian cuisine has amazing options",
            "potential_saving": "~0.8 kg CO₂e per meal replaced",
            "icon": "🥗",
            "priority": 1,
        },
        {
            "tip": "Reduce food waste — plan meals and use leftovers creatively",
            "potential_saving": "~0.5-1 kg CO₂e per day",
            "icon": "🍱",
            "priority": 2,
        },
        {
            "tip": "Buy local and seasonal produce from your nearby sabzi mandi",
            "potential_saving": "~30% lower food transport emissions",
            "icon": "🛒",
            "priority": 3,
        },
        {
            "tip": "Reduce dairy consumption — try plant-based milks like almond or oat",
            "potential_saving": "~0.3-0.5 kg CO₂e per litre replaced",
            "icon": "🥛",
            "priority": 4,
        },
        {
            "tip": "Grow herbs and vegetables at home — even a small balcony garden helps",
            "potential_saving": "Reduces transport and packaging emissions",
            "icon": "🌿",
            "priority": 5,
        },
    ],
    "waste": [
        {
            "tip": "Segregate wet and dry waste — mandatory in most Indian cities since 2024",
            "potential_saving": "~50-70% reduction in landfill methane",
            "icon": "♻️",
            "priority": 1,
        },
        {
            "tip": "Compost kitchen waste at home — great for your garden",
            "potential_saving": "~85% lower emissions than landfill",
            "icon": "🌱",
            "priority": 2,
        },
        {
            "tip": "Carry your own cloth bag — India's single-use plastic ban means less waste",
            "potential_saving": "~0.03 kg CO₂e per bag avoided",
            "icon": "👜",
            "priority": 3,
        },
        {
            "tip": "Donate or sell old electronics instead of discarding them",
            "potential_saving": "Significant reduction in e-waste emissions",
            "icon": "📱",
            "priority": 4,
        },
        {
            "tip": "Use a steel water bottle instead of buying packaged water",
            "potential_saving": "~14 kg CO₂e saved per year",
            "icon": "🫗",
            "priority": 5,
        },
    ],
    "water": [
        {
            "tip": "Fix leaky taps — a single drip wastes ~20 litres per day",
            "potential_saving": "~7,000 litres saved per year",
            "icon": "🔧",
            "priority": 1,
        },
        {
            "tip": "Take shorter showers — 5 minutes instead of 10 saves ~45 litres",
            "potential_saving": "Reduces water heating energy too",
            "icon": "🚿",
            "priority": 2,
        },
        {
            "tip": "Use a bucket instead of running water for washing dishes",
            "potential_saving": "~40-60 litres saved per wash",
            "icon": "🪣",
            "priority": 3,
        },
        {
            "tip": "Install a rainwater harvesting system — mandatory in many Indian states",
            "potential_saving": "Offsets ~30-50% of household water usage",
            "icon": "🌧️",
            "priority": 4,
        },
        {
            "tip": "Water your garden in the early morning to reduce evaporation",
            "potential_saving": "~25% less water needed",
            "icon": "🌅",
            "priority": 5,
        },
    ],
}


def get_personalized_tips(entry_breakdown, max_tips=5):
    """
    Generate personalized tips based on the user's carbon footprint.

    Distributes tips across categories, prioritizing the highest-emitting categories
    and returning a diverse, representative set of advice.

    Args:
        entry_breakdown: dict with keys 'transport', 'energy', 'food', 'waste', 'water'
                        containing CO₂e values in kg
        max_tips: Maximum number of tips to return (default: 5)

    Returns:
        list of dicts, each containing 'category', 'tip', 'potential_saving', 'icon'
    """
    valid_categories = [
        (cat, co2) for cat, co2 in entry_breakdown.items()
        if cat in TIPS_DATABASE
    ]

    # Sort categories by emission amount (highest first)
    sorted_categories = sorted(
        valid_categories,
        key=lambda x: x[1],
        reverse=True,
    )

    tips = []
    # Distribute tips using a round-robin approach over sorted categories to avoid over-indexing on a single area
    for tip_index in range(5):  # Each category in database has up to 5 tips
        for category, _ in sorted_categories:
            if len(tips) >= max_tips:
                break
            
            category_tips = TIPS_DATABASE[category]
            if tip_index < len(category_tips):
                tip_data = category_tips[tip_index]
                tips.append({
                    "category": category.title(),
                    "tip": tip_data["tip"],
                    "potential_saving": tip_data["potential_saving"],
                    "icon": tip_data["icon"],
                })
        if len(tips) >= max_tips:
            break

    return tips


def get_comparison_insight(total_co2):
    """
    Compare user's footprint against India and global averages.

    Args:
        total_co2: User's total daily CO₂e in kg

    Returns:
        dict with comparison data and message
    """
    india_diff = total_co2 - INDIA_DAILY_AVERAGE
    percentage_of_india = (total_co2 / INDIA_DAILY_AVERAGE) * 100 if INDIA_DAILY_AVERAGE > 0 else 0

    if total_co2 <= INDIA_DAILY_AVERAGE * 0.5:
        message = "Excellent! Your footprint is well below India's average. You're a climate champion! 🏆"
        level = "excellent"
    elif total_co2 <= INDIA_DAILY_AVERAGE:
        message = "Good job! Your footprint is below India's average. Keep improving! 🌟"
        level = "good"
    elif total_co2 <= INDIA_DAILY_AVERAGE * 1.5:
        message = "Your footprint is slightly above average. Small changes can make a big difference! 💪"
        level = "average"
    else:
        message = "Your footprint is significantly above average. Let's work on reducing it together! 🌍"
        level = "high"

    return {
        "total": round(total_co2, 2),
        "india_average": INDIA_DAILY_AVERAGE,
        "difference": round(india_diff, 2),
        "percentage_of_india": round(percentage_of_india, 1),
        "message": message,
        "level": level,
    }
