from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import engine, get_db, Base
from api.auth import verify_api_key
from api.pydantic_schemas import EventBatch
import api.crud as crud

app = FastAPI()

# MARK: GET
@app.get("/")
def root(key: str = Depends(verify_api_key)):
    return {"message": "Hello! Look at http://localhost:8000/docs for documentation."}

@app.get("/analytics/devices/breakdown")
def get_device_breakdown(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    number_of_devices = crud.get_absolute_number_of_devices(db)
    percentage_of_devices = crud.get_percentage_of_devices(db)

    return {"number_of_devices": number_of_devices,
            "percentage_of_devices": percentage_of_devices}

# MARK: POST
@app.post("/events/batch", status_code=status.HTTP_200_OK)
def add_event_batch(batch: EventBatch, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    crud.create_event(db, batch)
