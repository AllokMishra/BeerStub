from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from ..crud import get_dispense_logs
from datetime import datetime, timedelta, date
from typing import Optional

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/dispense", response_model=list[schemas.DispenseLog])
def get_dispense_report(
    machine_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    logs = get_dispense_logs(
        db,
        machine_id=machine_id,
        channel_id=channel_id,
        start_date=start_datetime,
        end_date=end_datetime,
        skip=skip,
        limit=limit
    )
    return logs

@router.get("/summary")
def get_summary_report(
    period: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    else:  # month
        start_date = now - timedelta(days=30)
    
    # This would be replaced with actual summary query
    return {
        "period": period,
        "start_date": start_date,
        "end_date": now,
        "total_dispensed_ml": 0,  # Placeholder
        "total_dispenses": 0,     # Placeholder
        "by_channel": []          # Placeholder
    }