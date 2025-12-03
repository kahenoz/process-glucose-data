import json
import pandas as pd
import json
from sqlalchemy.orm import Session
from clearbio_api.models.glucose_metrics_model import GlucoseMetrics


def save_user_metrics(user_id: int, metrics: dict, db: Session):
    """
    Saves metrics for a single user into the glucose_metrics table.
    """
    record = GlucoseMetrics(
        user_id=user_id,
        avg_glucose=metrics["avg_glucose"],
        tir=metrics["tir"],
        tar=metrics["tar"],
        tbr=metrics["tbr"],
        daily_variability=metrics["daily_variability"],
        num_days=metrics["num_days"],
        num_readings=metrics["num_readings"],
        json_summary=json.dumps(metrics),
        pdf_path=None,
    )
    db.add(record)


def compute_single_user_metrics(df: pd.DataFrame) -> dict:
    """
    df contains only rows for 1 user.
    """
    avg_glucose = df["glucose_mmol"].mean()

    tir = (df["glucose_mmol"].between(3.9, 10)).mean() * 100
    tar = (df["glucose_mmol"] > 10).mean() * 100
    tbr = (df["glucose_mmol"] < 3.9).mean() * 100

    num_readings = df.shape[0]
    num_days = df["timestamp"].dt.date.nunique()

    # Daily variability
    df["date"] = df["timestamp"].dt.date
    daily_sd = df.groupby("date")["glucose_mmol"].std()
    daily_variability = (
        daily_sd.mean() if len(daily_sd) > 0 else None
    )

    # 7-day trend (week-over-week)
    df["week"] = df["timestamp"].dt.to_period("W").apply(lambda x: x.start_time)
    weekly_avg = df.groupby("week")["glucose_mmol"].mean().sort_index()

    if len(weekly_avg) >= 2:
        trend_7day = weekly_avg.iloc[-1] - weekly_avg.iloc[-2]
    else:
        trend_7day = None

    return {
        "avg_glucose": round(avg_glucose, 2),
        "tir": round(tir, 2),
        "tar": round(tar, 2),
        "tbr": round(tbr, 2),
        "daily_variability": round(float(daily_variability), 3) if daily_variability is not None else None,
        "num_readings": int(num_readings),
        "num_days": int(num_days),
        "trend_7day": round(trend_7day, 2) if trend_7day is not None else None,
        "daily_sd_list": {str(k): float(v) for k, v in daily_sd.to_dict().items()}
    }


def compute_metrics_for_all_users(df: pd.DataFrame, db) -> dict:
    """
    Input DataFrame must contain:
        user_id, timestamp, glucose_mmol
    """

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["user_id", "timestamp"])

    # --- PROCESS EACH USER SEPARATELY ---
    for user_id, user_df in df.groupby("user_id"):
        metrics = compute_single_user_metrics(user_df)
        save_user_metrics(user_id, metrics, db)
    
    db.commit()

