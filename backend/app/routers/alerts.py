from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import District, Alert
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    MarkAlertsReadResponse,
    TestSMSAlertRequest,
    TestSMSAlertResponse
)
from app.services.sms_service import SMSService

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])


@router.get("", response_model=AlertListResponse)
def get_alerts(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(50, ge=1, le=200, description="Max alerts to retrieve"),
    db: Session = Depends(get_db)
):
    """Retrieve list of system alerts with read status and unread counter."""
    query = db.query(Alert).join(District, Alert.district_id == District.id, isouter=True)

    unread_count = db.query(Alert).filter(Alert.is_read.is_(False)).count()

    if unread_only:
        query = query.filter(Alert.is_read.is_(False))

    total = query.count()
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

    items = [
        AlertResponse(
            id=a.id,
            district_id=a.district_id,
            district_name=a.district.name if a.district else None,
            state_name=a.district.state.name if a.district and a.district.state else None,
            title=a.title,
            message=a.message,
            severity=a.severity,
            is_read=a.is_read,
            created_at=a.created_at.strftime("%d %b %Y, %I:%M %p") if a.created_at else ""
        )
        for a in alerts
    ]

    return AlertListResponse(
        total=total,
        unread_count=unread_count,
        alerts=items
    )


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an individual alert as read."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()
    db.refresh(alert)

    return AlertResponse(
        id=alert.id,
        district_id=alert.district_id,
        district_name=alert.district.name if alert.district else None,
        state_name=alert.district.state.name if alert.district and alert.district.state else None,
        title=alert.title,
        message=alert.message,
        severity=alert.severity,
        is_read=alert.is_read,
        created_at=alert.created_at.strftime("%d %b %Y, %I:%M %p") if alert.created_at else ""
    )


@router.post("/mark-all-read", response_model=MarkAlertsReadResponse)
def mark_all_alerts_read(db: Session = Depends(get_db)):
    """Mark all system alerts as read."""
    unread_alerts = db.query(Alert).filter(Alert.is_read.is_(False)).all()
    count = len(unread_alerts)

    for a in unread_alerts:
        a.is_read = True

    db.commit()

    return MarkAlertsReadResponse(
        message="All alerts have been marked as read.",
        updated_count=count
    )


@router.post("/test-sms", response_model=TestSMSAlertResponse)
def trigger_test_sms_alert(
    req: TestSMSAlertRequest,
    db: Session = Depends(get_db)
):
    """Manually trigger or test an agriculture officer SMS alert."""
    district = None
    if req.district_id:
        district = db.query(District).filter(District.id == req.district_id).first()
    elif req.district_name:
        district = db.query(District).filter(District.name.ilike(req.district_name.strip())).first()

    district_name = district.name if district else (req.district_name or "Ludhiana")
    state_name = (district.state.name if district and district.state else None) or req.state_name or "Punjab"
    officer_phone = req.phone or (getattr(district, "officer_phone", None) if district else None) or "+919876543210"

    message = SMSService.format_alert_message(
        district_name=district_name,
        state_name=state_name,
        horizon_days=req.horizon_days
    )

    sms_res = SMSService.send_sms(
        phone=officer_phone,
        message=message,
        district_name=district_name,
        state_name=state_name
    )

    new_alert = Alert(
        district_id=district.id if district else None,
        title=f"Manual/Test SMS Alert: {district_name} ({state_name})",
        message=message,
        severity="High",
        is_read=False
    )
    db.add(new_alert)
    db.commit()

    return TestSMSAlertResponse(
        success=sms_res.get("success", True),
        mode=sms_res.get("mode", "demo"),
        recipient=officer_phone,
        district=district_name,
        state=state_name,
        message=message,
        alert_created=True,
        note=sms_res.get("note", "Alert saved to inbox and sent via SMS service.")
    )
