from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DistrictBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    officer_name: Optional[str] = "Agriculture Development Officer"
    officer_phone: Optional[str] = "+919876543210"


class DistrictResponse(DistrictBase):
    id: int
    state_id: int
    state_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StateBase(BaseModel):
    name: str
    code: str


class StateResponse(StateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StateWithDistrictsResponse(StateResponse):
    districts: List[DistrictResponse] = []

    model_config = ConfigDict(from_attributes=True)


class StatesDistrictsHierarchyResponse(BaseModel):
    states: List[StateWithDistrictsResponse]
