import io
from clearbio_api.utils.helper import add_users
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from clearbio_api.database.get_db import get_db_session
from clearbio_api.models.glucose_data_model import GlucoseData
import pandas as pd

from clearbio_api.services.upload_data_service import compute_metrics_for_all_users

router = APIRouter()

@router.post("/upload-data")
async def upload_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    required_columns = {"user_id", "timestamp", "glucose_mmol"}

    try:
        contents = await file.read()

        # Try reading CSV
        try:
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid CSV format. File could not be parsed."
            )
        
        add_users(df, db)

        # Check required columns
        missing = required_columns - set(df.columns)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required columns: {', '.join(missing)}"
            )

        # Convert timestamp column
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Timestamp column has invalid format."
            )

        # Insert rows
        for _, row in df.iterrows():
            entry = GlucoseData(
                user_id=row["user_id"],
                timestamp=row["timestamp"],
                glucose_mmol=row["glucose_mmol"]
            )
            db.add(entry)

        db.commit()
        distinct_users = df["user_id"].nunique()

        compute_metrics_for_all_users(df, db)

        return {
            "status": "success",
            "processed_users": distinct_users
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
