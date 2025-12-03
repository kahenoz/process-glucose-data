from clearbio_api.utils.helper import get_user_or_404
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from clearbio_api.database.get_db import get_db_session
from clearbio_api.models.glucose_data_model import GlucoseData

router = APIRouter()


@router.get("/trends/{user_id}")
async def get_7day_trend(user_id: int, db: Session = Depends(get_db_session)):
    """
    Return 7-day glucose trend for a given user_id.
    """
    get_user_or_404(user_id, db)
    try:
        # Get the last 7 days of data
        subquery = (
            db.query(
                func.date(GlucoseData.timestamp).label("day"),
                func.avg(GlucoseData.glucose_mmol).label("mean_glucose")
            )
            .filter(GlucoseData.user_id == user_id)
            .group_by(func.date(GlucoseData.timestamp))
            .order_by(func.date(GlucoseData.timestamp).desc())
            .limit(7)
            .subquery()
        )

        # Query again to order days ascending
        trend_rows = db.query(subquery).order_by(subquery.c.day.asc()).all()

        if not trend_rows:
            return {"message": f"No glucose data found for user_id {user_id}"}

        trend = [
            {"day": str(row.day), "mean_glucose": round(row.mean_glucose, 2)}
            for row in trend_rows
        ]

        return {"trend": trend}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
