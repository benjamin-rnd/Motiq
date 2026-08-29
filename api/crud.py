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

    # return is not needed, because after receiving events the API just answers with 201 CREATED (in case of Success)
    # return db_events

# MARK: Read
def get_number_of_events_by_name(db: Session, event_name: str) -> int:
    return len(db.query(EventModel).where(EventModel.event_name == event_name).all())

def get_daily_active_users(db: Session) -> int:
    return db.execute(
        text("""
            SELECT count(DISTINCT user_id)
            FROM events
            WHERE date(timestamp) = DATE('now')
        """)
    ).scalar() or 0

def get_monthly_active_users(db: Session) -> int:
    return db.execute(
        text("""
            SELECT count(DISTINCT user_id)
            FROM events
            WHERE timestamp >= datetime('now', '-30 days')
        """)
    ).scalar() or 0

def get_new_vs_returning_users(db: Session, number_of_days: int) -> dict[str, dict[str, int | float]]:
    row = db.execute(
        text(f"""
            SELECT
                COUNT(DISTINCT CASE WHEN first_seen >= datetime('now', '-{number_of_days} days') THEN user_id END) AS new_users,
                COUNT(DISTINCT CASE WHEN first_seen < datetime('now', '-{number_of_days} days') THEN user_id END) AS returning_users
            FROM (
                SELECT user_id, min(timestamp) as first_seen
                FROM events
                GROUP BY user_id
            )
            WHERE user_id IN (
                SELECT DISTINCT user_id
                FROM events
                WHERE timestamp >= datetime('now', '-{number_of_days} days')
            )
        """)
    ).fetchone()

    if row is None:
        return {"absolute": {}, "percentage": {}}

    absolute: dict[str, int | float] = {
        "new_users": row.new_users,
        "returning_users": row.returning_users
    }

    total = sum(absolute.values())
    if total == 0:
        return {"absolute": {}, "percentage": {}}
    
    percentages: dict[str, int | float] = {k: round(v / total * 100, 1) for k, v in absolute.items()}

    return {"absolute": absolute,
            "percentage": percentages}

def get_retention(db: Session) -> list[dict[str, int | float]]:
    retention = []
    for week in range(1, 5):
        row = db.execute(
            text(f"""
                SELECT 
                    count(DISTINCT user_id) AS cohort_size, 
                    count(DISTINCT CASE WHEN user_id IN (
                        SELECT DISTINCT user_id FROM events
                        WHERE timestamp >= datetime('now', '-7 days')
                    ) THEN user_id END) AS retained
                FROM (
                    SELECT user_id, min(timestamp) AS first_seen
                    FROM events
                    GROUP BY user_id
                )
                WHERE first_seen >= datetime('now', '-{week * 7} days')
                AND first_seen < datetime('now', '-{(week - 1) * 7} days')
            """)
        ).fetchone()

        if row is None:
            continue

        cohort_size = row.cohort_size
        retained = row.retained
        percentage = round(retained / cohort_size * 100, 1) if cohort_size > 0 else 0.0

        retention.append({
            "week": week,
            "cohort_size": cohort_size,
            "retained": retained,
            "percentage": percentage
        })

    return retention

def get_avg_duration_per_session(db: Session) -> float:
    return db.execute(
        text("""
            SELECT round(avg(duration_seconds), 1) AS avg_duration_seconds
            FROM (
                SELECT session_id, (julianday(MAX(timestamp)) - julianday(MIN(timestamp))) * 86400 AS duration_seconds
                FROM events
                WHERE event_name IN ("app_launched", "app_closed")
                GROUP BY session_id
            )
        """)
    ).scalar() or 0.0

def get_avg_sessions(db: Session, number_of_days: int) -> float:
    return db.execute(
        text(f"""
            SELECT round(count(DISTINCT session_id) / {number_of_days}.0, 1)
            FROM events
            WHERE timestamp >= datetime("now", "-{number_of_days} days")
        """)
    ).scalar() or 0.0

def get_sessions_today(db: Session) -> int:
    return db.execute(
        text("""
            SELECT count(DISTINCT session_id)
            FROM events
            WHERE date(timestamp) = date("now")
        """)
    ).scalar() or 0

def get_property_breakdown(db: Session, property_name: str) -> dict[str, dict[str, int | float]]:
    rows = db.execute(
        text(f"""
            SELECT {property_name}, count(*) AS total
            FROM (
                SELECT DISTINCT user_id, json_extract(properties, "$.{property_name}") AS {property_name}
                FROM events
                WHERE event_name = "app_launched"
            )
            GROUP BY {property_name}
        """)
    ).all()

    absolute: dict[str, int | float] = {getattr(row, property_name): row.total for row in rows}

    total = sum(absolute.values())
    if total == 0:
        return {"absolute": {}, "percentage": {}}
    
    percentages: dict[str, int | float] = {k: round(v / total * 100, 1) for k, v in absolute.items()}

    return {"absolute": absolute,
            "percentage": percentages}

def get_accessbility_features(db: Session) -> dict[str, dict[str, int | float]]:
    rows = db.execute(
        text("""
            SELECT value AS accessibility_features, count(DISTINCT user_id) AS total
            FROM events, json_each(json_extract(properties, "$.accessibility_features"))
            WHERE event_name = "app_launched"
            GROUP BY value
        """)
    ).all()
    
    absolute: dict[str, int | float] = {row.accessibility_features: row.total for row in rows}

    total = sum(absolute.values())
    if total == 0:
        return {"absolute": {}, "percentage": {}}

    percentages: dict[str, int | float] = {k: round(v / total * 100, 1) for k, v in absolute.items()}

    return {"absolute": absolute,
            "percentage": percentages}