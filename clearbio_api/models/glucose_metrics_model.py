from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.sql import func
from clearbio_api.database.get_db import Base

class GlucoseMetrics(Base):
    __tablename__ = "glucose_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer)

    avg_glucose = Column(Float)
    tir = Column(Float)
    tar = Column(Float) #time above range
    tbr = Column(Float) #time below range

    daily_variability = Column(Float)

    num_days = Column(Integer)
    num_readings = Column(Integer)

    json_summary = Column(Text)
    pdf_path = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
