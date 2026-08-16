from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

import api.crud as crud
from api.auth import verify_api_key, verify_hmac_signature, verify_timestamp
from api.database import Base, engine, get_db
from api.orm_models import Event
from api.pydantic_schemas import EventBatch

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Base.metadata.create_all(bind = engine)
    yield
    # shutdown

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

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
@app.get("/analytics/devices/breakdown", status_code=status.HTTP_200_OK)
def get_device_breakdown(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    number_of_devices = crud.get_absolute_number_of_devices(db)
    percentage_of_devices = crud.get_percentage_of_devices(db)

    if number_of_devices == {}:
        return "No devices found"

    return {"number_of_devices": number_of_devices,
            "percentage_of_devices": percentage_of_devices}
