import datetime as dt
from typing import List, Optional

from ..domain.models import Habit
from .database import Database


class HabitRepository:
    """习惯持久化，封装 CRUD 与简单查询。"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, habit: Habit) -> Habit:
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO habits(name, description, category, target_per_week, enabled, created_at)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                habit.name,
                habit.description,
                habit.category,
                habit.target_per_week,
                1 if habit.enabled else 0,
                habit.created_at.isoformat(),
            ),
        )
        habit.id = cursor.lastrowid
        self.db.connect().commit()
        return habit

    def update(self, habit: Habit) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            """
            UPDATE habits
            SET name=?, description=?, category=?, target_per_week=?, enabled=?
            WHERE id=?
            """,
            (
                habit.name,
                habit.description,
                habit.category,
                habit.target_per_week,
                1 if habit.enabled else 0,
                habit.id,
            ),
        )
        self.db.connect().commit()

    def delete(self, habit_id: int) -> None:
        """硬删除，相关记录通过 ON DELETE CASCADE 同步删除。"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
        self.db.connect().commit()

    def get(self, habit_id: int) -> Optional[Habit]:
        row = self.db.cursor().execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
        return self._to_model(row) if row else None

    def list_all(self, enabled_only: bool = False) -> List[Habit]:
        cursor = self.db.cursor()
        if enabled_only:
            rows = cursor.execute("SELECT * FROM habits WHERE enabled=1 ORDER BY created_at DESC").fetchall()
        else:
            rows = cursor.execute("SELECT * FROM habits ORDER BY created_at DESC").fetchall()
        return [self._to_model(r) for r in rows]

    def _to_model(self, row) -> Habit:
        return Habit(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            category=row["category"],
            target_per_week=row["target_per_week"],
            enabled=bool(row["enabled"]),
            created_at=dt.datetime.fromisoformat(row["created_at"]),
        )
