from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import State, District, RiskPrediction, FireDetection
from app.schemas.analytics import OverviewStatsResponse, FireTrendsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])


@router.get("/overview-stats", response_model=OverviewStatsResponse)
def get_overview_stats(
    state: Optional[str] = Query(None, description="Filter by state (e.g. Punjab, Haryana)"),
    db: Session = Depends(get_db)
):
    """Compute the 5 core dashboard KPI metrics dynamically from the database."""
    # Filter districts by state if requested
    district_query = db.query(District).join(State)
    if state and state.strip() and state.lower() not in ["all", "punjab & haryana"]:
        district_query = district_query.filter(State.name.ilike(f"%{state.strip()}%"))
    
    district_ids = [d.id for d in district_query.all()]
    total_districts = len(district_ids)

    # Subquery: get latest prediction ID per district
    high_count = 0
    med_count = 0
    low_count = 0

    if district_ids:
        subquery = (
            db.query(
                RiskPrediction.district_id,
                func.max(RiskPrediction.id).label("max_id")
            )
            .filter(RiskPrediction.district_id.in_(district_ids))
            .group_by(RiskPrediction.district_id)
            .subquery()
        )

        latest_preds = (
            db.query(RiskPrediction)
            .join(subquery, RiskPrediction.id == subquery.c.max_id)
            .all()
        )

        for p in latest_preds:
            if p.risk_level == "High":
                high_count += 1
            elif p.risk_level == "Medium":
                med_count += 1
            else:
                low_count += 1

    # 7-day fire detections count
    max_fire_date = db.query(func.max(FireDetection.detection_date)).scalar() or date.today()
    start_date = max_fire_date - timedelta(days=6)

    fire_query = db.query(FireDetection).filter(FireDetection.detection_date >= start_date)
    if district_ids:
        fire_query = fire_query.filter(FireDetection.district_id.in_(district_ids))
    active_fires = fire_query.count()

    return OverviewStatsResponse(
        high_risk_districts=high_count,
        medium_risk_districts=med_count,
        low_risk_districts=low_count,
        total_districts=total_districts,
        active_fire_detections_7d=active_fires,
        forecast_period="3–5 days",
        state_filter=state if state else "All",
        last_updated=datetime.now().strftime("%d %b %Y, %H:%M")
    )


@router.get("/fire-trends", response_model=FireTrendsResponse)
def get_fire_trends(
    days: int = Query(7, ge=3, le=30, description="Number of past days for fire trend"),
    db: Session = Depends(get_db)
):
    """Return daily aggregated satellite fire counts by date and state for the bar chart."""
    max_fire_date = db.query(func.max(FireDetection.detection_date)).scalar() or date.today()
    start_date = max_fire_date - timedelta(days=days - 1)

    # Generate dates sequence
    dates_list = [start_date + timedelta(days=i) for i in range(days)]
    date_strs = [d.isoformat() for d in dates_list]
    labels = [d.strftime("%d %b").lstrip("0") for d in dates_list]

    punjab_counts = {d: 0 for d in dates_list}
    haryana_counts = {d: 0 for d in dates_list}

    # Query fire detections grouped by date and state
    results = (
        db.query(
            FireDetection.detection_date,
            State.name,
            func.count(FireDetection.id)
        )
        .join(District, FireDetection.district_id == District.id, isouter=True)
        .join(State, District.state_id == State.id, isouter=True)
        .filter(FireDetection.detection_date >= start_date)
        .group_by(FireDetection.detection_date, State.name)
        .all()
    )

    for d_date, s_name, count in results:
        if d_date in punjab_counts:
            if s_name == "Punjab":
                punjab_counts[d_date] += count
            elif s_name == "Haryana":
                haryana_counts[d_date] += count

    p_vals = [punjab_counts[d] for d in dates_list]
    h_vals = [haryana_counts[d] for d in dates_list]
    totals = [p + h for p, h in zip(p_vals, h_vals)]

    return FireTrendsResponse(
        labels=labels,
        dates=date_strs,
        punjab=p_vals,
        haryana=h_vals,
        total=totals
    )
