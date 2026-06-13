from pydantic import BaseModel
from typing import Any

class EventBatch(BaseModel):
    events: list[Event]

class Event(BaseModel):
    event_name: str
    user_id: str
    session_id: str
    timestamp: str
    properties: dict[str, Any] = {}