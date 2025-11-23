import datetime as dt
from typing import Dict, List, Optional

from ..domain.models import HabitRecord
from ..utils.dates import iso_date
from .database import Database


class HabitRecordRepository:
    """每日打卡记录的持久化封装。"""

    def __init__(self, db: Database):
        self.db = db

    def upsert(
        self, habit_id: int, date: dt.date, is_completed: bool, note: str = ""
    ) -> HabitRecord:
        """插入或更新指定日期的完成状态。"""
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO habit_records(habit_id, date, is_completed, note, recorded_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(habit_id, date) DO UPDATE SET is_completed=excluded.is_completed, note=excluded.note
            """,
            (
                habit_id,
                iso_date(date),
                1 if is_completed else 0,
                note,
                dt.datetime.utcnow().isoformat(),
            ),
        )
        self.db.connect().commit()
        record_id = cursor.lastrowid
        return HabitRecord(
            id=record_id if record_id != 0 else self.get_by_habit_date(habit_id, date).id,
            habit_id=habit_id,
            date=date,
            is_completed=is_completed,
            note=note,
        )

    def get_by_habit_date(self, habit_id: int, date: dt.date) -> Optional[HabitRecord]:
        row = self.db.cursor().execute(
            "SELECT * FROM habit_records WHERE habit_id=? AND date=?", (habit_id, iso_date(date))
        ).fetchone()
        if not row:
            return None
        return HabitRecord(
            id=row["id"],
            habit_id=row["habit_id"],
            date=dt.date.fromisoformat(row["date"]),
            is_completed=bool(row["is_completed"]),
            note=row["note"],
            recorded_at=dt.datetime.fromisoformat(row["recorded_at"]),
        )

    def fetch_by_habit_and_range(
        self, habit_id: int, start: dt.date, end: dt.date
    ) -> List[HabitRecord]:
        rows = self.db.cursor().execute(
            """
            SELECT * FROM habit_records
            WHERE habit_id=? AND date BETWEEN ? AND ?
            ORDER BY date ASC
            """,
            (habit_id, iso_date(start), iso_date(end)),
        ).fetchall()
        return [
            HabitRecord(
                id=r["id"],
                habit_id=r["habit_id"],
                date=dt.date.fromisoformat(r["date"]),
                is_completed=bool(r["is_completed"]),
                note=r["note"],
                recorded_at=dt.datetime.fromisoformat(r["recorded_at"]),
            )
            for r in rows
        ]

    def stats_completed_count(self, habit_id: int, days: int) -> int:
        start = dt.date.today() - dt.timedelta(days=days - 1)
        row = self.db.cursor().execute(
            """
            SELECT COUNT(*) as cnt FROM habit_records
            WHERE habit_id=? AND date>=? AND is_completed=1
            """,
            (habit_id, iso_date(start)),
        ).fetchone()
        return row["cnt"] if row else 0

    def fetch_recent_dates(self, habit_id: int, limit: int = 30) -> Dict[str, bool]:
        rows = self.db.cursor().execute(
            """
            SELECT date, is_completed FROM habit_records
            WHERE habit_id=?
            ORDER BY date DESC LIMIT ?
            """,
            (habit_id, limit),
        ).fetchall()
        return {r["date"]: bool(r["is_completed"]) for r in rows}

    def all_by_habit(self, habit_id: int):
        rows = self.db.cursor().execute(
            """
            SELECT * FROM habit_records
            WHERE habit_id=?
            ORDER BY date ASC
            """,
            (habit_id,),
        ).fetchall()
        return [
            HabitRecord(
                id=r["id"],
                habit_id=r["habit_id"],
                date=dt.date.fromisoformat(r["date"]),
                is_completed=bool(r["is_completed"]),
                note=r["note"],
                recorded_at=dt.datetime.fromisoformat(r["recorded_at"]),
            )
            for r in rows
        ]
