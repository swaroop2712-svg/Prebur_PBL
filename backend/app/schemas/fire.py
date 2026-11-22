from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FireDetectionItem(BaseModel):
    id: int
    detection_date: str
    district: str
    state: str
    satellite: str
    confidence: str
    frp: float
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class FireListResponse(BaseModel):
    total: int
    page: int
    limit: int
    fires: List[FireDetectionItem]
