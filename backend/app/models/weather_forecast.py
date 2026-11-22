from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, default=date.today, index=True)
    temperature = Column(Float, nullable=False)  # Celsius
    humidity = Column(Float, nullable=False)     # Percentage
    wind_speed = Column(Float, nullable=False)   # km/h
    condition = Column(String(50), nullable=False)  # Sunny, Partly Cloudy, Rain, etc.

    # Relationships
    district = relationship("District", back_populates="weather_forecasts")
