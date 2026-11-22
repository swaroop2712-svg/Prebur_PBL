from typing import List
from pydantic import BaseModel


class OverviewStatsResponse(BaseModel):
    high_risk_districts: int
    medium_risk_districts: int
    low_risk_districts: int
    total_districts: int
    active_fire_detections_7d: int
    forecast_period: str = "3–5 days"
    state_filter: str = "All"
    last_updated: str


class FireTrendsResponse(BaseModel):
    labels: List[str]  # e.g., ["9 Oct", "10 Oct", ...]
    dates: List[str]   # e.g., ["2025-10-09", ...]
    punjab: List[int]
    haryana: List[int]
    total: List[int]
