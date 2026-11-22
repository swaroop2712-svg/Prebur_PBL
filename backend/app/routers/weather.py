from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import District, WeatherForecast
from app.schemas.weather import DistrictWeatherResponse, WeatherDayForecast

router = APIRouter(prefix="/weather", tags=["Weather"])

ICON_MAP = {
    "Sunny": "☀️",
    "Clear": "☀️",
    "Partly Cloudy": "🌤️",
    "Cloudy": "☁️",
    "Rain": "🌧️",
    "Thunderstorm": "⛈️"
}


@router.get("/{district_id}", response_model=DistrictWeatherResponse)
def get_district_weather(district_id: int, db: Session = Depends(get_db)):
    """Fetch 4-day meteorological outlook for a specific district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    forecasts = (
        db.query(WeatherForecast)
        .filter(WeatherForecast.district_id == district.id)
        .order_by(WeatherForecast.forecast_date.asc())
        .limit(4)
        .all()
    )

    day_labels = ["Today", "Tomorrow", "Day 3", "Day 4"]
    items = []

    if forecasts:
        for i, f in enumerate(forecasts):
            label = day_labels[i] if i < len(day_labels) else f.forecast_date.strftime("%d %b")
            icon = ICON_MAP.get(f.condition, "🌤️")
            items.append(
                WeatherDayForecast(
                    forecast_date=f.forecast_date.isoformat(),
                    day_label=label,
                    icon=icon,
                    temperature=f.temperature,
                    humidity=f.humidity,
                    wind_speed=f.wind_speed,
                    condition=f.condition
                )
            )
    else:
        # Fallback generated 4-day forecast if records don't exist yet
        today = date.today()
        default_temps = [30.0, 29.0, 28.0, 26.0]
        conditions = ["Sunny", "Sunny", "Partly Cloudy", "Rain"]

        for i in range(4):
            f_date = today + timedelta(days=i)
            cond = conditions[i]
            items.append(
                WeatherDayForecast(
                    forecast_date=f_date.isoformat(),
                    day_label=day_labels[i],
                    icon=ICON_MAP.get(cond, "🌤️"),
                    temperature=default_temps[i],
                    humidity=float(48 + i * 7),
                    wind_speed=float(max(4, 12 - i * 2)),
                    condition=cond
                )
            )

    return DistrictWeatherResponse(
        district_id=district.id,
        district_name=district.name,
        state_name=district.state.name if district.state else "",
        forecasts=items
    )
