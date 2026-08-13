from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from api.database import Base, engine, get_db
from api.auth import verify_api_key
from api.pydantic_schemas import EventBatch
from api.orm_models import Event
import api.crud as crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Base.metadata.create_all(bind = engine)
    yield
    # shutdown

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# MARK: GET
@app.get("/analytics/devices/breakdown", status_code=status.HTTP_200_OK)
def get_device_breakdown(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    number_of_devices = crud.get_absolute_number_of_devices(db)
    percentage_of_devices = crud.get_percentage_of_devices(db)

    if number_of_devices == {}:
        return "No devices found"

    return {"number_of_devices": number_of_devices,
            "percentage_of_devices": percentage_of_devices}

# MARK: POST
@app.post("/events/batch", status_code=status.HTTP_201_CREATED)
def add_event_batch(batch: EventBatch, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    crud.create_event(db, batch)
