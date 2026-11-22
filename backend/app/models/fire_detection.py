from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FireDetection(Base):
    __tablename__ = "fire_detections"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True, index=True)
    detection_date = Column(Date, nullable=False, default=date.today, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    satellite = Column(String(50), nullable=False)  # e.g., VIIRS SNPP, VIIRS NOAA-20, MODIS
    confidence = Column(String(20), nullable=False)  # High, Nominal, Low
    frp = Column(Float, nullable=False)  # Fire Radiative Power in MW

    # Relationships
    district = relationship("District", back_populates="fire_detections")
