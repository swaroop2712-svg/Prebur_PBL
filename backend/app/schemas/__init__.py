from app.schemas.geo import (
    DistrictBase,
    DistrictResponse,
    StateBase,
    StateResponse,
    StateWithDistrictsResponse,
    StatesDistrictsHierarchyResponse,
)
from app.schemas.analytics import OverviewStatsResponse, FireTrendsResponse
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    DistrictRiskItem,
    LatestPredictionsResponse,
)
from app.schemas.fire import FireDetectionItem, FireListResponse
from app.schemas.weather import WeatherDayForecast, DistrictWeatherResponse
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    MarkAlertsReadResponse,
)

__all__ = [
    "DistrictBase",
    "DistrictResponse",
    "StateBase",
    "StateResponse",
    "StateWithDistrictsResponse",
    "StatesDistrictsHierarchyResponse",
    "OverviewStatsResponse",
    "FireTrendsResponse",
    "PredictionRequest",
    "PredictionResponse",
    "DistrictRiskItem",
    "LatestPredictionsResponse",
    "FireDetectionItem",
    "FireListResponse",
    "WeatherDayForecast",
    "DistrictWeatherResponse",
    "AlertResponse",
    "AlertListResponse",
    "MarkAlertsReadResponse",
]
