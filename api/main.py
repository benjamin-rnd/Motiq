from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import api.crud as crud
from api.auth import verify_api_key, verify_hmac_signature, verify_timestamp
from api.database import Base, engine, get_db, get_readonly_db
from api.orm_models import Event
from api.pydantic_schemas import EventBatch

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Base.metadata.create_all(bind = engine)
    yield
    # shutdown

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["null"],
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)

# MARK: POST
@app.post("/events/batch", status_code=status.HTTP_201_CREATED)
async def add_event_batch(request: Request, batch: EventBatch, db: Session = Depends(get_db)):
    timestamp = request.headers.get("X-Timestamp")
    signature = request.headers.get("X-Signature")
    if not timestamp or not signature:
        raise HTTPException(status_code=401, detail="Missing authentication headers")

    timestamp_valid = verify_timestamp(timestamp)
    if timestamp_valid == False:
        raise HTTPException(status_code=401, detail="Expired timestamp")

    raw_body = await request.body()

    signature_valid = verify_hmac_signature(signature, timestamp, raw_body)
    if signature_valid == False:
        raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        crud.create_event(db, batch)

# MARK: GET
@app.get("/analytics/users/active", status_code=status.HTTP_200_OK)
def get_dau_mau(db: Session = Depends(get_readonly_db), key: str = Depends(verify_api_key)):
    return {"dau": crud.get_daily_active_users(db),
            "mau": crud.get_monthly_active_users(db)}

@app.get("/analytics/users/new-vs-returning", status_code=status.HTTP_200_OK)
def get_new_vs_returning_users(days: int, db: Session = Depends(get_readonly_db), key: str = Depends(verify_api_key)):
    return crud.get_new_vs_returning_users(db, days)

@app.get("/analytics/sessions/summary", status_code=status.HTTP_200_OK)
def get_session_summary(db: Session = Depends(get_readonly_db), key: str = Depends(verify_api_key)):
    return {
        "sessions_today": crud.get_sessions_today(db),
        "avg_sessions_last_7d": crud.get_avg_sessions(db, 7),
        "avg_sessions_last_30d": crud.get_avg_sessions(db, 30),
        "avg_duration_per_session": crud.get_avg_duration_per_session(db)
    }

@app.get("/analytics/devices/breakdown", status_code=status.HTTP_200_OK)
def get_device_breakdown(db: Session = Depends(get_readonly_db), key: str = Depends(verify_api_key)):
    return crud.get_property_breakdown(db, "device_model")

@app.get("/analytics/environment/breakdown", status_code=status.HTTP_200_OK)
def get_environment_breakdown(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    return {
        "os_version": crud.get_property_breakdown(db, "os_version"),
        "color_scheme": crud.get_property_breakdown(db, "color_scheme"),
        "orientation": crud.get_property_breakdown(db, "orientation"),
        "connectivity": crud.get_property_breakdown(db, "connectivity"),
        "accessibility_features": crud.get_accessbility_features(db)
    }
