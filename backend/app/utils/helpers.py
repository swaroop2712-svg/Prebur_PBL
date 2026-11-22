from datetime import date, datetime
from typing import Tuple


def calculate_risk_level(probability: float) -> str:
    """Classify risk level from probability percentage."""
    if probability >= 65.0:
        return "High"
    elif probability >= 40.0:
        return "Medium"
    else:
        return "Low"


def get_risk_window_label(horizon_days: int) -> str:
    """Format human-readable window label."""
    return f"Elevated risk within {horizon_days} days"


def format_date_str(d: date | datetime) -> str:
    """Standardized date string YYYY-MM-DD."""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    return d.isoformat()
