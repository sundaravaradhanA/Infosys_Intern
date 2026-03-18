from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from app.schemas import AlertCreate, AlertResponse

router = APIRouter()

@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    user_id: int = Query(1, description="User ID"),
    unread_only: bool = Query(False, description="Show only unread alerts"),
    db: Session = Depends(get_db)
):
    """Get all alerts for a user"""
    query = db.query(Alert).filter(Alert.user_id == user_id)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    return query.order_by(Alert.created_at.desc()).all()

@router.post("/", response_model=AlertResponse)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
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

@router.patch("/{alert_id}/mark-read")
def mark_alert_as_read(
    alert_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Mark an alert as read"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}

@router.patch("/mark-all-read")
def mark_all_alerts_as_read(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Mark all alerts as read for a user"""
    db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All alerts marked as read"}

@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}

@router.get("/unread-count")
def get_unread_count(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get count of unread alerts"""
    count = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_read == False
    ).count()
    return {"unread_count": count}
