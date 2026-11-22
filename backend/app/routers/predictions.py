from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import State, District, RiskPrediction
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    DistrictRiskItem,
    LatestPredictionsResponse
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Risk Predictions"])


@router.get("/latest", response_model=LatestPredictionsResponse)
def get_latest_predictions(
    state: Optional[str] = Query(None, description="Filter by state (e.g. Punjab, Haryana)"),
    horizon_days: int = Query(3, ge=1, le=14, description="Horizon days filter"),
    db: Session = Depends(get_db)
):
    """Fetch latest risk prediction for each district, ordered by probability descending."""
    district_query = db.query(District).join(State)
    if state and state.strip() and state.lower() not in ["all", "punjab & haryana"]:
        district_query = district_query.filter(State.name.ilike(f"%{state.strip()}%"))

    district_ids = [d.id for d in district_query.all()]
    if not district_ids:
        return LatestPredictionsResponse(total=0, horizon_days=horizon_days, predictions=[])

    # Get latest prediction record for each district matching horizon_days
    subquery = (
        db.query(
            RiskPrediction.district_id,
            func.max(RiskPrediction.id).label("max_id")
        )
        .filter(RiskPrediction.district_id.in_(district_ids))
        .filter(RiskPrediction.horizon_days == horizon_days)
        .group_by(RiskPrediction.district_id)
        .subquery()
    )

    preds = (
        db.query(RiskPrediction)
        .join(subquery, RiskPrediction.id == subquery.c.max_id)
        .join(District, RiskPrediction.district_id == District.id)
        .join(State, District.state_id == State.id)
        .order_by(RiskPrediction.probability.desc())
        .all()
    )

    items = [
        DistrictRiskItem(
            district_id=p.district_id,
            district=p.district.name,
            state=p.district.state.name if p.district and p.district.state else "",
            risk_level=p.risk_level,
            probability=p.probability,
            prediction_date=p.prediction_date.isoformat(),
            horizon_days=p.horizon_days
        )
        for p in preds
    ]

    return LatestPredictionsResponse(
        total=len(items),
        horizon_days=horizon_days,
        predictions=items
    )


@router.post("/predict", response_model=PredictionResponse)
def predict_risk(req: PredictionRequest, db: Session = Depends(get_db)):
    """Run stubble burning prediction for a given district and forecast horizon."""
    return PredictionService.run_prediction(db, req)
