from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, default=date.today, index=True)
    horizon_days = Column(Integer, nullable=False, default=3)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)  # High, Medium, Low
    created_at = Column(DateTime, default=func.now())

    # Relationships
    district = relationship("District", back_populates="risk_predictions")
