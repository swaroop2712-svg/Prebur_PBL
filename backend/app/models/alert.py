from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="High")  # High, Medium, Low, Info
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), index=True)

    # Relationships
    district = relationship("District", back_populates="alerts")
