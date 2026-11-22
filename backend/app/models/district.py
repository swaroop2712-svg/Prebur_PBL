from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    officer_name = Column(String(100), nullable=True, default="Agriculture Development Officer")
    officer_phone = Column(String(20), nullable=True, default="+919876543210")

    # Relationships
    state = relationship("State", back_populates="districts")
    risk_predictions = relationship("RiskPrediction", back_populates="district", cascade="all, delete-orphan")
    fire_detections = relationship("FireDetection", back_populates="district", cascade="all, delete-orphan")
    weather_forecasts = relationship("WeatherForecast", back_populates="district", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="district", cascade="all, delete-orphan")
