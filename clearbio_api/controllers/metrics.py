from clearbio_api.utils.helper import get_user_or_404
from sqlalchemy.orm import Session
from clearbio_api.database.get_db import get_db_session
from clearbio_api.models.glucose_metrics_model import GlucoseMetrics
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/metrics/{user_id}")
async def display_glucose_metrics(user_id: int, db: Session = Depends(get_db_session)):
    get_user_or_404(user_id, db)
    try:
        rows = (
            db.query(GlucoseMetrics)
            .filter_by(user_id=user_id)
            .order_by(GlucoseMetrics.created_at.desc())
            .all()
        )

        if not rows:
            return {"message": f"No metrics found for user_id {user_id}"}

        result = [
            {
                "id": row.id,
                "user_id": row.user_id,
                "avg_glucose": row.avg_glucose,
                "tir": row.tir,
                "tar": row.tar,
                "tbr": row.tbr,
                "daily_variability": row.daily_variability,
                "num_days": row.num_days,
                "num_readings": row.num_readings,
                "json_summary": row.json_summary,
                "pdf_path": row.pdf_path,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
