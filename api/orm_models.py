from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(nullable=False)
    session_id: Mapped[str] = mapped_column(nullable=False)
    app_id: Mapped[str] = mapped_column(nullable=True)
    timestamp: Mapped[str] = mapped_column(nullable=False)
    properties: Mapped[str] = mapped_column(default="{}")

    __table_args__ = (
        Index("ix-event_name-user_id", "event_name", "user_id"),
    )