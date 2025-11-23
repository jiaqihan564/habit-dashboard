import datetime as dt
from typing import List, Optional

from ..domain.models import Habit
from .database import Database


def now_utc_iso():
    """获取当前 UTC 时间的 ISO 格式字符串。"""
    return dt.datetime.now(dt.timezone.utc).isoformat()


class HabitRepository:
    """习惯定义的持久化层，封装数据库操作细节。"""

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
                habit.enabled,
                now_utc_iso(),
            ),
        )
        self.db.connect().commit()
        habit.id = cursor.lastrowid
        return habit

    def update(self, habit: Habit) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            """
            UPDATE habits SET
                name=?, description=?, category=?, target_per_week=?, enabled=?
            WHERE id=?
            """,
            (
                habit.name,
                habit.description,
                habit.category,
                habit.target_per_week,
                habit.enabled,
                habit.id,
            ),
        )
        self.db.connect().commit()

    def soft_delete(self, habit_id: int) -> None:
        """软删除：打标 deleted_at，保留历史记录。"""
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE habits SET enabled=0, deleted_at=? WHERE id=?",
            (now_utc_iso(), habit_id),
        )
        self.db.connect().commit()

    def get(self, habit_id: int, include_deleted: bool = False) -> Optional[Habit]:
        sql = "SELECT * FROM habits WHERE id=?"
        params = [habit_id]
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        row = self.db.cursor().execute(sql, params).fetchone()
        return self._to_model(row) if row else None

    def list_all(self, enabled_only: bool = False, include_deleted: bool = False) -> List[Habit]:
        cursor = self.db.cursor()
        clauses = []
        params = []
        if enabled_only:
            clauses.append("enabled=1")
        if not include_deleted:
            clauses.append("deleted_at IS NULL")
        where = ""
        if clauses:
            where = "WHERE " + " AND ".join(clauses)
        rows = cursor.execute(f"SELECT * FROM habits {where} ORDER BY created_at DESC", params).fetchall()
        return [self._to_model(r) for r in rows]

    def _to_model(self, row) -> Habit:
        return Habit(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            category=row["category"],
            target_per_week=row["target_per_week"],
            enabled=bool(row["enabled"]),
            created_at=dt.datetime.fromisoformat(row["created_at"]).replace(tzinfo=dt.timezone.utc) if row["created_at"] else dt.datetime.now(dt.timezone.utc),
            deleted_at=dt.datetime.fromisoformat(row["deleted_at"]).replace(tzinfo=dt.timezone.utc) if row["deleted_at"] else None,
        )