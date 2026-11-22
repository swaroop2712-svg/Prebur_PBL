from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import State, District, FireDetection
from app.schemas.fire import FireDetectionItem, FireListResponse

router = APIRouter(prefix="/fires", tags=["Fire Detections"])


@router.get("", response_model=FireListResponse)
def get_fires(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    search: Optional[str] = Query(None, description="Search district, state, or satellite"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page"),
    export_csv: bool = Query(False, description="Export filtered records as CSV download"),
    db: Session = Depends(get_db)
):
    """Retrieve satellite fire detections with filtering and search capabilities."""
    query = (
        db.query(FireDetection)
        .join(District, FireDetection.district_id == District.id, isouter=True)
        .join(State, District.state_id == State.id, isouter=True)
    )

    if state and state.strip() and state.lower() not in ["all", "all states"]:
        query = query.filter(State.name.ilike(f"%{state.strip()}%"))

    if district_id:
        query = query.filter(FireDetection.district_id == district_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (District.name.ilike(term)) |
            (State.name.ilike(term)) |
            (FireDetection.satellite.ilike(term))
        )

    total = query.count()

    # If CSV export requested
    if export_csv:
        detections = query.order_by(FireDetection.detection_date.desc()).all()
        csv_lines = ["Date,District,State,Satellite,Confidence,FRP,Latitude,Longitude"]
        for d in detections:
            dist_name = d.district.name if d.district else "Unknown"
            state_name = d.district.state.name if d.district and d.district.state else "Unknown"
            csv_lines.append(
                f"{d.detection_date.isoformat()},{dist_name},{state_name},{d.satellite},{d.confidence},{d.frp},{d.latitude},{d.longitude}"
            )
        csv_content = "\n".join(csv_lines)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=preburn_fires.csv"}
        )

    # Paginated JSON response
    offset = (page - 1) * limit
    detections = query.order_by(FireDetection.detection_date.desc()).offset(offset).limit(limit).all()

    items = [
        FireDetectionItem(
            id=d.id,
            detection_date=d.detection_date.isoformat(),
            district=d.district.name if d.district else "Unknown",
            state=d.district.state.name if d.district and d.district.state else "Unknown",
            satellite=d.satellite,
            confidence=d.confidence,
            frp=d.frp,
            latitude=d.latitude,
            longitude=d.longitude
        )
        for d in detections
    ]

    return FireListResponse(
        total=total,
        page=page,
        limit=limit,
        fires=items
    )
