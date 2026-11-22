from app.routers.geo import router as geo_router
from app.routers.analytics import router as analytics_router
from app.routers.predictions import router as predictions_router
from app.routers.fires import router as fires_router
from app.routers.weather import router as weather_router
from app.routers.alerts import router as alerts_router

__all__ = [
    "geo_router",
    "analytics_router",
    "predictions_router",
    "fires_router",
    "weather_router",
    "alerts_router"
]
