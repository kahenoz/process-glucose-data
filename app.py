from fastapi import FastAPI
from clearbio_api.database.get_db import Base, engine

# IMPORT MODELS BEFORE create_all()
from clearbio_api.models.users_model import Users
from clearbio_api.models.glucose_data_model import GlucoseData
from clearbio_api.models.glucose_metrics_model import GlucoseMetrics

Base.metadata.create_all(bind=engine)

from clearbio_api.controllers.upload_data import router as upload_data
from clearbio_api.controllers.metrics import router as metrics
from clearbio_api.controllers.trends import router as trends

app = FastAPI()

app.include_router(upload_data)
app.include_router(metrics)
app.include_router(trends)

@app.get("/", include_in_schema=False)
def root():
    return {"running": True}
