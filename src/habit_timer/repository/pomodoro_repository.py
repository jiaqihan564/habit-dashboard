import datetime as dt
from typing import List

from ..domain.models import PomodoroSession
from .database import Database


class PomodoroRepository:
    """番茄钟记录持久化。"""

    def __init__(self, db: Database):
        self.db = db

    def add_session(self, session: PomodoroSession) -> PomodoroSession:
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO pomodoro_sessions(habit_id, start_time, end_time, duration_seconds, status)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                session.habit_id,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                session.duration_seconds,
                session.status,
            ),
        )
        self.db.connect().commit()
        session.id = cursor.lastrowid
        return session

    def count_between(self, start: dt.datetime, end: dt.datetime) -> int:
        row = self.db.cursor().execute(
            """
            SELECT COUNT(*) as cnt FROM pomodoro_sessions
            WHERE start_time BETWEEN ? AND ? AND status='completed'
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchone()
        return row["cnt"] if row else 0

    def recent_sessions(self, limit: int = 20) -> List[PomodoroSession]:
        rows = self.db.cursor().execute(
            "SELECT * FROM pomodoro_sessions ORDER BY start_time DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            PomodoroSession(
                id=r["id"],
                habit_id=r["habit_id"],
                start_time=dt.datetime.fromisoformat(r["start_time"]),
                end_time=dt.datetime.fromisoformat(r["end_time"]) if r["end_time"] else None,
                duration_seconds=r["duration_seconds"],
                status=r["status"],
            )
            for r in rows
        ]
