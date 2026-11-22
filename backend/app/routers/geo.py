from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import State, District
from app.schemas.geo import (
    StatesDistrictsHierarchyResponse,
    StateWithDistrictsResponse,
    DistrictResponse
)

router = APIRouter(prefix="/geo", tags=["Geography"])


@router.get("/states-districts", response_model=StatesDistrictsHierarchyResponse)
def get_states_and_districts(db: Session = Depends(get_db)):
    """Fetch complete hierarchical list of states and their corresponding districts."""
    states = db.query(State).order_by(State.name).all()
    result = []
    for s in states:
        dists = [
            DistrictResponse(
                id=d.id,
                state_id=d.state_id,
                state_name=s.name,
                name=d.name,
                latitude=d.latitude,
                longitude=d.longitude
            )
            for d in s.districts
        ]
        result.append(StateWithDistrictsResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            districts=dists
        ))
    return StatesDistrictsHierarchyResponse(states=result)


@router.get("/districts", response_model=List[DistrictResponse])
def get_districts(
    state: Optional[str] = Query(None, description="Filter by state name (e.g. Punjab, Haryana)"),
    db: Session = Depends(get_db)
):
    """Fetch districts with optional state filter."""
    query = db.query(District).join(State)
    if state and state.strip() and state.lower() != "all":
        query = query.filter(State.name.ilike(f"%{state.strip()}%"))

    districts = query.order_by(District.name).all()
    return [
        DistrictResponse(
            id=d.id,
            state_id=d.state_id,
            state_name=d.state.name,
            name=d.name,
            latitude=d.latitude,
            longitude=d.longitude
        )
        for d in districts
    ]
