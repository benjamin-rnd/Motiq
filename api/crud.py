import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from api.orm_models import Event as EventModel
from api.pydantic_schemas import EventBatch, Event as EventSchema

# MARK: Create
def create_event(db: Session, event_batch: EventBatch):
    db_events = []

    for event in event_batch.events:
        db_event = EventModel(
            event_name = event.event_name,
            user_id = event.user_id,
            session_id = event.session_id,
            app_id = event.app_id,
            timestamp = event.timestamp,
            properties = json.dumps(event.properties)
        )
        db_events.append(db_event)

    db.add_all(db_events)
    db.commit()

    # return is not needed, because after receiving events the API just answers with 200 OK
    # return db_events

# MARK: Read
def get_number_of_events_by_name(db: Session, event_name: str) -> int:
    return len(db.query(EventModel).where(EventModel.event_name == event_name).all())

def get_absolute_number_of_devices(db: Session) -> dict[str, int]:
    result = db.execute(
        text("""
            SELECT json_extract(properties, '$.device_model') as device_model, COUNT(DISTINCT user_id) as count
            FROM events
            WHERE event_name = 'app_launched'
            GROUP BY device_model
            ORDER BY count DESC
        """)
    )

    return {
        str(device_model): int(count)
        for device_model, count in result.all()
    }

def get_percentage_of_devices(db: Session) -> dict[str, float]:
    result = db.execute(
        text("""
            SELECT json_extract(properties, '$.device_model') as device_model, COUNT(DISTINCT user_id) as count
            FROM events
            WHERE event_name = 'app_launched'
            GROUP BY device_model
        """)
    )
    rows = result.all()

    total_devices = 0
    for device_model, count in rows:
        total_devices += count

    if total_devices == 0:
        return {}
    
    percentages: dict[str, float] = {}

    for device_model, count in rows:
        percentage = (count / total_devices) * 100
        percentages[device_model] = round(percentage, 1)

    return percentages
