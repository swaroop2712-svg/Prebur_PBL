from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class WeatherDayForecast(BaseModel):
    forecast_date: str
    day_label: str  # "Today", "Tomorrow", "Day 3", "Day 4"
    icon: str       # "☀️", "🌤️", "🌧️"
    temperature: float
    humidity: float
    wind_speed: float
    condition: str

    model_config = ConfigDict(from_attributes=True)


class DistrictWeatherResponse(BaseModel):
    district_id: int
    district_name: str
    state_name: str
    forecasts: List[WeatherDayForecast]
