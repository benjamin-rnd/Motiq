"""
Motiq – dynamische Test-Datengenerierung
Wird als pytest-Fixture (scope="session") in conftest.py eingebunden.
Alle Timestamps sind relativ zu datetime.utcnow(), damit Analytics-Queries
wie DATE('now') und datetime('now', '-7 days') korrekt funktionieren.

Kohortenverteilung (für Retention-Tests):
    Woche 4 (vor  0– 7 Tagen): User 01–05  → alle auch heute aktiv   (100 %)
    Woche 3 (vor  8–14 Tagen): User 06–10  → 4 von 5 diese Woche     ( 80 %)
    Woche 2 (vor 15–21 Tagen): User 11–15  → 3 von 5 diese Woche     ( 60 %)
    Woche 1 (vor 22–28 Tagen): User 16–20  → 2 von 5 diese Woche     ( 40 %)
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

def seed(db: Session) -> None:
    now = datetime.now(timezone.utc)

    def ts(delta: timedelta) -> str:
        return (now + delta).strftime("%Y-%m-%dT%H:%M:%SZ")

    def ago(**kwargs) -> timedelta:
        return -timedelta(**kwargs)

    # helper function: add complete app launch and close
    def session_events(
        user_id: str,
        session_id: str,
        launch_delta: timedelta,
        duration_minutes: int,
        device_model: str,
        os_version: str,
        color_scheme: str,
        orientation: str,
        connectivity: str,
        accessibility_features: list[str],
        extra_events: list[dict] | None = None,
    ) -> list[dict]:
        launch_ts = ts(launch_delta)
        close_ts = ts(launch_delta + timedelta(minutes=duration_minutes))
        props = {
            "device_model": device_model,
            "os_version": os_version,
            "app_version": "1.0.0",
            "color_scheme": color_scheme,
            "orientation": orientation,
            "connectivity": connectivity,
            "accessibility_features": accessibility_features,
        }
        events = [
            {"event_name": "app_launched", "user_id": user_id, "session_id": session_id, "timestamp": launch_ts, "properties": props},
        ]
        if extra_events:
            events.extend(extra_events)
        events.append(
            {"event_name": "app_backgrounded", "user_id": user_id, "session_id": session_id, "timestamp": close_ts, "properties": {}}
        )
        return events

    all_events: list[dict] = []

    # MARK: Week 4 - first active 0-7 days ago
    # User 01 - 3F2A... iPhone 15 Pro, dark, wifi, 2 sessions
    all_events += session_events(
        "3F2A1B4C-D5E6-7890-ABCD-EF1234567890", "A1B2C3D4-E5F6-7890-ABCD-111111111111",
        ago(hours=3), 8,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "wifi", [],
        extra_events=[
            {"event_name": "view_appeared", "user_id": "3F2A1B4C-D5E6-7890-ABCD-EF1234567890", "session_id": "A1B2C3D4-E5F6-7890-ABCD-111111111111", "timestamp": ts(ago(hours=3) + timedelta(seconds=5)), "properties": {"screen": "home"}},
            {"event_name": "button_tapped", "user_id": "3F2A1B4C-D5E6-7890-ABCD-EF1234567890", "session_id": "A1B2C3D4-E5F6-7890-ABCD-111111111111", "timestamp": ts(ago(hours=3) + timedelta(seconds=40)), "properties": {"button_id": "explore_button", "screen": "home"}},
        ]
    )
    all_events += session_events(
        "3F2A1B4C-D5E6-7890-ABCD-EF1234567890", "A1B2C3D4-E5F6-7890-ABCD-111111111112",
        ago(hours=1), 5,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "cellular", [],
    )

    # User 02 - 7C8D... iPhone 14, light, wifi, larger_text
    all_events += session_events(
        "7C8D9E0F-A1B2-3456-CDEF-222222222222", "B2C3D4E5-F6A7-8901-BCDE-222222222221",
        ago(hours=2), 10,
        "iPhone 14", "18.2", "light", "portrait", "wifi", ["larger_text"],
        extra_events=[
            {"event_name": "button_tapped", "user_id": "7C8D9E0F-A1B2-3456-CDEF-222222222222", "session_id": "B2C3D4E5-F6A7-8901-BCDE-222222222221", "timestamp": ts(ago(hours=2) + timedelta(minutes=1)), "properties": {"button_id": "purchase_button", "screen": "shop"}},
        ]
    )

    # User 03 - 1A2B... iPhone 15, dark, wifi, voiceover + larger_text
    all_events += session_events(
        "1A2B3C4D-E5F6-7890-ABCD-333333333333", "C3D4E5F6-A7B8-9012-CDEF-333333333331",
        ago(hours=4), 7,
        "iPhone 15", "18.3", "dark", "portrait", "wifi", ["voiceover", "larger_text"],
        extra_events=[
            {"event_name": "view_appeared", "user_id": "1A2B3C4D-E5F6-7890-ABCD-333333333333", "session_id": "C3D4E5F6-A7B8-9012-CDEF-333333333331", "timestamp": ts(ago(hours=4) + timedelta(seconds=5)), "properties": {"screen": "onboarding"}},
            {"event_name": "button_tapped", "user_id": "1A2B3C4D-E5F6-7890-ABCD-333333333333", "session_id": "C3D4E5F6-A7B8-9012-CDEF-333333333331", "timestamp": ts(ago(hours=4) + timedelta(minutes=1)), "properties": {"button_id": "onboarding_complete", "screen": "onboarding"}},
        ]
    )

    # User 04 - 9E8D... iPhone 13, light, cellular, 2 sessions
    all_events += session_events(
        "9E8D7C6B-A5F4-3210-FEDC-444444444444", "D4E5F6A7-B8C9-0123-DEFA-444444444441",
        ago(hours=5), 6,
        "iPhone 13", "18.1", "light", "portrait", "cellular", [],
    )
    all_events += session_events(
        "9E8D7C6B-A5F4-3210-FEDC-444444444444", "D4E5F6A7-B8C9-0123-DEFA-444444444442",
        ago(hours=1, minutes=30), 8,
        "iPhone 13", "18.1", "light", "landscape", "wifi", [],
        extra_events=[
            {"event_name": "button_tapped", "user_id": "9E8D7C6B-A5F4-3210-FEDC-444444444444", "session_id": "D4E5F6A7-B8C9-0123-DEFA-444444444442", "timestamp": ts(ago(hours=1, minutes=30) + timedelta(minutes=1)), "properties": {"button_id": "purchase_button", "screen": "shop"}},
        ]
    )

    # User 05 - B1C2... iPhone 15 Pro, dark, wifi, reduce_motion
    all_events += session_events(
        "B1C2D3E4-F5A6-7890-BCDE-555555555555", "E5F6A7B8-C9D0-1234-EFAB-555555555551",
        ago(hours=2, minutes=30), 5,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "wifi", ["reduce_motion"],
    )

    # MARK: Week 3 - first active 8-14 days ago
    # User 06 - C2D3... iPhone 14, light, wifi
    all_events += session_events(
        "C2D3E4F5-A6B7-8901-CDEF-666666666666", "F6A7B8C9-D0E1-2345-FABC-666666666661",
        ago(days=10), 8,
        "iPhone 14", "18.2", "light", "portrait", "wifi", [],
        extra_events=[
            {"event_name": "button_tapped", "user_id": "C2D3E4F5-A6B7-8901-CDEF-666666666666", "session_id": "F6A7B8C9-D0E1-2345-FABC-666666666661", "timestamp": ts(ago(days=10) + timedelta(minutes=1)), "properties": {"button_id": "purchase_button", "screen": "shop"}},
        ]
    )
    all_events += session_events(
        "C2D3E4F5-A6B7-8901-CDEF-666666666666", "F6A7B8C9-D0E1-2345-FABC-666666666662",
        ago(days=2), 6,
        "iPhone 14", "18.2", "light", "portrait", "wifi", [],
    )

    # User 07 - D3E4... iPhone 13, dark, wifi, bold_text
    all_events += session_events(
        "D3E4F5A6-B7C8-9012-DEFA-777777777777", "A7B8C9D0-E1F2-3456-ABCD-777777777771",
        ago(days=12), 6,
        "iPhone 13", "18.1", "dark", "portrait", "wifi", ["bold_text"],
    )
    all_events += session_events(
        "D3E4F5A6-B7C8-9012-DEFA-777777777777", "A7B8C9D0-E1F2-3456-ABCD-777777777772",
        ago(days=3), 4,
        "iPhone 13", "18.1", "dark", "portrait", "wifi", ["bold_text"],
    )

    # User 08 - E4F5... iPhone 15, light, cellular
    all_events += session_events(
        "E4F5A6B7-C8D9-0123-EFAB-888888888888", "B8C9D0E1-F2A3-4567-BCDE-888888888881",
        ago(days=9), 5,
        "iPhone 15", "18.3", "light", "portrait", "cellular", [],
    )
    all_events += session_events(
        "E4F5A6B7-C8D9-0123-EFAB-888888888888", "B8C9D0E1-F2A3-4567-BCDE-888888888882",
        ago(hours=6), 7,
        "iPhone 15", "18.3", "light", "portrait", "cellular", [],
    )

    # User 09 - F5A6... iPhone 15 Pro, dark, wifi
    all_events += session_events(
        "F5A6B7C8-D9E0-1234-FABC-999999999999", "C9D0E1F2-A3B4-5678-CDEF-999999999991",
        ago(days=11), 9,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "wifi", [],
    )
    all_events += session_events(
        "F5A6B7C8-D9E0-1234-FABC-999999999999", "C9D0E1F2-A3B4-5678-CDEF-999999999992",
        ago(days=1), 5,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "wifi", [],
    )

    # User 10 - A6B7... iPhone 14, light, wifi, larger_text + reduce_motion
    all_events += session_events(
        "A6B7C8D9-E0F1-2345-ABCD-AAAAAAAAAAAA", "D0E1F2A3-B4C5-6789-DEFA-AAAAAAAAAAAA",
        ago(days=13), 7,
        "iPhone 14", "18.2", "light", "portrait", "wifi", ["larger_text", "reduce_motion"],
    )

    # MARK: Week 2 - first active 15-21 days ago
    # User 11 - B7C8... iPhone 13, dark, wifi
    all_events += session_events(
        "B7C8D9E0-F1A2-3456-BCDE-BBBBBBBBBBBB", "E1F2A3B4-C5D6-7890-EFAB-BBBBBBBBBBBB",
        ago(days=18), 6,
        "iPhone 13", "18.1", "dark", "portrait", "wifi", [],
        extra_events=[
            {"event_name": "button_tapped", "user_id": "B7C8D9E0-F1A2-3456-BCDE-BBBBBBBBBBBB", "session_id": "E1F2A3B4-C5D6-7890-EFAB-BBBBBBBBBBBB", "timestamp": ts(ago(days=18) + timedelta(minutes=1)), "properties": {"button_id": "settings_button", "screen": "home"}},
            {"event_name": "button_tapped", "user_id": "B7C8D9E0-F1A2-3456-BCDE-BBBBBBBBBBBB", "session_id": "E1F2A3B4-C5D6-7890-EFAB-BBBBBBBBBBBB", "timestamp": ts(ago(days=18) + timedelta(minutes=2)), "properties": {"button_id": "notifications_toggle", "screen": "settings"}},
        ]
    )
    all_events += session_events(
        "B7C8D9E0-F1A2-3456-BCDE-BBBBBBBBBBBB", "E1F2A3B4-C5D6-7890-EFAB-BBBBBBBBBBBC",
        ago(days=4), 5,
        "iPhone 13", "18.1", "dark", "portrait", "wifi", [],
    )

    # User 12 - C8D9... iPhone 16, light, wifi
    all_events += session_events(
        "C8D9E0F1-A2B3-4567-CDEF-CCCCCCCCCCCC", "F2A3B4C5-D6E7-8901-FABC-CCCCCCCCCCCC",
        ago(days=20), 12,
        "iPhone 16", "18.4", "light", "portrait", "wifi", [],
    )
    all_events += session_events(
        "C8D9E0F1-A2B3-4567-CDEF-CCCCCCCCCCCC", "F2A3B4C5-D6E7-8901-FABC-CCCCCCCCCCCD",
        ago(days=5), 8,
        "iPhone 16", "18.4", "light", "portrait", "wifi", [],
    )

    # User 13 - D9E0... iPhone 16 Pro, dark, cellular
    all_events += session_events(
        "D9E0F1A2-B3C4-5678-DEFA-DDDDDDDDDDDD", "A3B4C5D6-E7F8-9012-ABCD-DDDDDDDDDDDD",
        ago(days=16), 9,
        "iPhone 16 Pro", "18.4", "dark", "portrait", "cellular", ["bold_text"],
    )
    all_events += session_events(
        "D9E0F1A2-B3C4-5678-DEFA-DDDDDDDDDDDD", "A3B4C5D6-E7F8-9012-ABCD-DDDDDDDDDDDE",
        ago(hours=8), 6,
        "iPhone 16 Pro", "18.4", "dark", "portrait", "cellular", ["bold_text"],
    )

    # User 14 - E0F1... iPhone 15, light, wifi
    all_events += session_events(
        "E0F1A2B3-C4D5-6789-EFAB-EEEEEEEEEEEE", "B4C5D6E7-F8A9-0123-BCDE-EEEEEEEEEEEE",
        ago(days=17), 5,
        "iPhone 15", "18.3", "light", "portrait", "wifi", [],
    )

    # User 15 - F1A2... iPhone 14, dark, wifi
    all_events += session_events(
        "F1A2B3C4-D5E6-7890-FABC-FFFFFFFFFFFF", "C5D6E7F8-A9B0-1234-CDEF-FFFFFFFFFFFF",
        ago(days=19), 4,
        "iPhone 14", "18.2", "dark", "landscape", "wifi", ["larger_text"],
    )

    # MARK: Week 1 - first active 22-28 days ago
    # User 16 - A2B3... iPhone 13 Pro, dark, wifi
    all_events += session_events(
        "A2B3C4D5-E6F7-8901-ABCD-111111111110", "D6E7F8A9-B0C1-2345-DEFA-111111111110",
        ago(days=25), 10,
        "iPhone 13 Pro", "18.1", "dark", "portrait", "wifi", ["reduce_motion"],
    )
    all_events += session_events(
        "A2B3C4D5-E6F7-8901-ABCD-111111111110", "D6E7F8A9-B0C1-2345-DEFA-111111111111",
        ago(days=6), 7,
        "iPhone 13 Pro", "18.1", "dark", "portrait", "wifi", ["reduce_motion"],
    )

    # User 17 - B3C4... iPhone 16, light, cellulars
    all_events += session_events(
        "B3C4D5E6-F7A8-9012-BCDE-222222222220", "E7F8A9B0-C1D2-3456-EFAB-222222222220",
        ago(days=27), 8,
        "iPhone 16", "18.4", "light", "portrait", "cellular", [],
    )
    all_events += session_events(
        "B3C4D5E6-F7A8-9012-BCDE-222222222220", "E7F8A9B0-C1D2-3456-EFAB-222222222221",
        ago(days=2), 9,
        "iPhone 16", "18.4", "light", "portrait", "cellular", [],
    )

    # User 18 - C4D5... iPhone 15 Pro, dark, wifi
    all_events += session_events(
        "C4D5E6F7-A8B9-0123-CDEF-333333333330", "F8A9B0C1-D2E3-4567-FABC-333333333330",
        ago(days=23), 6,
        "iPhone 15 Pro", "18.3", "dark", "portrait", "wifi", [],
    )

    # User 19 - D5E6... iPhone 14, light, wifi
    all_events += session_events(
        "D5E6F7A8-B9C0-1234-DEFA-444444444440", "A9B0C1D2-E3F4-5678-ABCD-444444444440",
        ago(days=26), 5,
        "iPhone 14", "18.2", "light", "portrait", "wifi", ["larger_text"],
    )

    # User 20 - E6F7... iPhone 13, dark, cellular
    all_events += session_events(
        "E6F7A8B9-C0D1-2345-EFAB-555555555550", "B0C1D2E3-F4A5-6789-BCDE-555555555550",
        ago(days=24), 7,
        "iPhone 13", "18.1", "dark", "portrait", "cellular", ["bold_text"],
    )

    # MARK: clear table and refill it
    db.execute(text("DELETE FROM events"))

    for event in all_events:
        import json
        db.execute(
            text("""
                INSERT INTO events (event_name, user_id, session_id, timestamp, properties)
                VALUES (:event_name, :user_id, :session_id, :timestamp, :properties)
            """),
            {
                "event_name": event["event_name"],
                "user_id": event["user_id"],
                "session_id": event["session_id"],
                "timestamp": event["timestamp"],
                "properties": json.dumps(event["properties"]),
            }
        )

    db.commit()
