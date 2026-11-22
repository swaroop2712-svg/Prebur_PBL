from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False)

    # Relationships
    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
