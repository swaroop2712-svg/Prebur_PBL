from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    district_id: Optional[int] = Field(None, description="Database ID of the district")
    district_name: Optional[str] = Field(None, description="Name of the district (e.g., Ludhiana)")
    state_name: Optional[str] = Field(None, description="Name of the state (Punjab or Haryana)")
    horizon_days: int = Field(3, ge=1, le=14, description="Forecast window in days (3, 4, 5, etc.)")


class PredictionResponse(BaseModel):
    district_id: int
    district_name: str
    state_name: str
    horizon_days: int
    probability: float
    risk_level: str  # High, Medium, Low
    risk_window: str
    prediction_date: str
    is_demo: bool = False
    confidence_interval: Optional[str] = "±4%"
    features_used: Optional[dict] = None
    officer_alert_dispatched: Optional[bool] = False
    officer_phone: Optional[str] = None
    sms_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DistrictRiskItem(BaseModel):
    district_id: int
    district: str
    state: str
    risk_level: str
    probability: float
    prediction_date: str
    horizon_days: int

    model_config = ConfigDict(from_attributes=True)


class LatestPredictionsResponse(BaseModel):
    total: int
    horizon_days: int
    predictions: List[DistrictRiskItem]
