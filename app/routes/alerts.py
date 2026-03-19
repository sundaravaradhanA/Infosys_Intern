from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Alert
from app.schemas import AlertCreate, AlertResponse
from app.services.alert_service import AlertService

# ❗ IMPORTANT: NO prefix here (fixes /alerts/alerts issue)
router = APIRouter(tags=["Alerts"])


# ================= GET ALERTS =================
@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    user_id: int = Query(1),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all alerts for a user"""
    query = db.query(Alert).filter(Alert.user_id == user_id)

    if unread_only:
        query = query.filter(Alert.is_read == False)

    return query.order_by(Alert.created_at.desc()).all()


# ================= GENERATE ALERTS =================
@router.post("/generate")
def generate_alerts(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Generate alerts (low balance, budget exceeded, bill due)"""
    service = AlertService(db)
    result = service.generate_all_alerts(user_id)

    return {
        "message": "Alerts generated successfully",
        "alerts_created": result["alerts_created"]
    }


# ================= CREATE ALERT =================
@router.post("/", response_model=AlertResponse)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a manual alert"""
    new_alert = Alert(
        user_id=alert.user_id,
        title=alert.title,
        message=alert.message,
        alert_type=alert.alert_type,
        is_read=False
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


# ================= MARK SINGLE READ =================
@router.patch("/{alert_id}/mark-read")
def mark_alert_as_read(
    alert_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()

    return {"message": "Alert marked as read"}


# ================= MARK ALL READ =================
@router.patch("/mark-all-read")
def mark_all_alerts_as_read(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    count = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_read == False
    ).update({"is_read": True})

    db.commit()

    return {
        "message": "All alerts marked as read",
        "updated_count": count
    }


# ================= DELETE ALERT =================
@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()

    return {"message": "Alert deleted successfully"}


# ================= UNREAD COUNT =================
@router.get("/unread-count")
def get_unread_count(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    count = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_read == False
    ).count()

    return {"unread_count": count}


# ================= UNREAD ALERTS =================
@router.get("/unread", response_model=List[AlertResponse])
def get_unread_alerts(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get only unread alerts"""
    return db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_read == False
    ).order_by(Alert.created_at.desc()).all()