import json
from pathlib import Path
from typing import Dict, List

from ..domain.models import AppConfig, Habit, HabitRecord, PomodoroSession
from ..repository.config_repository import ConfigRepository
from ..repository.habit_repository import HabitRepository
from ..repository.pomodoro_repository import PomodoroRepository
from ..repository.record_repository import HabitRecordRepository


class BackupService:
    """数据导出/导入，供设置页调用。"""

    def __init__(
        self,
        habit_repo: HabitRepository,
        record_repo: HabitRecordRepository,
        pomodoro_repo: PomodoroRepository,
        config_repo: ConfigRepository,
    ):
        self.habit_repo = habit_repo
        self.record_repo = record_repo
        self.pomodoro_repo = pomodoro_repo
        self.config_repo = config_repo

    def export_to_file(self, path: str | Path) -> None:
        data = {
            "habits": [self._habit_to_dict(h) for h in self.habit_repo.list_all(include_deleted=True)],
            "habit_records": [self._record_to_dict(r) for h in self.habit_repo.list_all(include_deleted=True) for r in self.record_repo.all_by_habit(h.id)],
            "pomodoros": [self._pomodoro_to_dict(p) for p in self.pomodoro_repo.recent_sessions(10000)],
            "config": self._config_to_dict(self.config_repo.load()),
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_from_file(self, path: str | Path, merge_strategy: str = "append") -> None:
        content = Path(path).read_text(encoding="utf-8")
        data = json.loads(content)
        conn = self.habit_repo.db.connect()
        cursor = conn.cursor()
        if merge_strategy == "replace":
            cursor.execute("DELETE FROM habit_records")
            cursor.execute("DELETE FROM pomodoro_sessions")
            cursor.execute("DELETE FROM habits")
        # 先导入 habits
        for h in data.get("habits", []):
            cursor.execute(
                """
                INSERT INTO habits(id, name, description, category, target_per_week, enabled, created_at, deleted_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    h.get("id"),
                    h["name"],
                    h.get("description", ""),
                    h.get("category", "其它"),
                    h.get("target_per_week", 7),
                    1 if h.get("enabled", True) else 0,
                    h.get("created_at"),
                    h.get("deleted_at"),
                ),
            )
        # 导入 habit_records
        for r in data.get("habit_records", []):
            cursor.execute(
                """
                INSERT OR IGNORE INTO habit_records(id, habit_id, date, is_completed, note, recorded_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    r.get("id"),
                    r["habit_id"],
                    r["date"],
                    1 if r.get("is_completed") else 0,
                    r.get("note", ""),
                    r.get("recorded_at"),
                ),
            )
        # 导入番茄
        for p in data.get("pomodoros", []):
            cursor.execute(
                """
                INSERT OR IGNORE INTO pomodoro_sessions(id, habit_id, start_time, end_time, duration_seconds, status)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    p.get("id"),
                    p.get("habit_id"),
                    p.get("start_time"),
                    p.get("end_time"),
                    p.get("duration_seconds", 0),
                    p.get("status", "completed"),
                ),
            )
        # 配置覆盖
        cfg = data.get("config")
        if cfg:
            cursor.execute(
                """
                INSERT INTO app_config(id, work_minutes, short_break_minutes, long_break_minutes, long_break_interval)
                VALUES(1, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    work_minutes=excluded.work_minutes,
                    short_break_minutes=excluded.short_break_minutes,
                    long_break_minutes=excluded.long_break_minutes,
                    long_break_interval=excluded.long_break_interval
                """,
                (
                    cfg.get("work_minutes", 25),
                    cfg.get("short_break_minutes", 5),
                    cfg.get("long_break_minutes", 15),
                    cfg.get("long_break_interval", 4),
                ),
            )
        conn.commit()

    def _habit_to_dict(self, habit: Habit) -> Dict:
        return {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "category": habit.category,
            "target_per_week": habit.target_per_week,
            "enabled": habit.enabled,
            "created_at": habit.created_at.isoformat(),
            "deleted_at": habit.deleted_at.isoformat() if habit.deleted_at else None,
        }

    def _record_to_dict(self, record: HabitRecord) -> Dict:
        return {
            "id": record.id,
            "habit_id": record.habit_id,
            "date": record.date.isoformat(),
            "is_completed": record.is_completed,
            "note": record.note,
            "recorded_at": record.recorded_at.isoformat() if record.recorded_at else None,
        }

    def _pomodoro_to_dict(self, p: PomodoroSession) -> Dict:
        return {
            "id": p.id,
            "habit_id": p.habit_id,
            "start_time": p.start_time.isoformat(),
            "end_time": p.end_time.isoformat() if p.end_time else None,
            "duration_seconds": p.duration_seconds,
            "status": p.status,
        }

    def _config_to_dict(self, cfg: AppConfig) -> Dict:
        return {
            "work_minutes": cfg.work_minutes,
            "short_break_minutes": cfg.short_break_minutes,
            "long_break_minutes": cfg.long_break_minutes,
            "long_break_interval": cfg.long_break_interval,
        }
