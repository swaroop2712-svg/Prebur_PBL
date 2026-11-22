from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: int
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    state_name: Optional[str] = None
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    total: int
    unread_count: int
    alerts: List[AlertResponse]


class MarkAlertsReadResponse(BaseModel):
    message: str
    updated_count: int


class TestSMSAlertRequest(BaseModel):
    district_id: Optional[int] = None
    district_name: Optional[str] = "Ludhiana"
    state_name: Optional[str] = "Punjab"
    phone: Optional[str] = None
    horizon_days: int = 3


class TestSMSAlertResponse(BaseModel):
    success: bool
    mode: str
    recipient: str
    district: str
    state: str
    message: str
    alert_created: bool
    note: Optional[str] = None
