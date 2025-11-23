import datetime as dt
from typing import Dict, Optional

from ..domain.models import PomodoroSession
from ..repository.pomodoro_repository import PomodoroRepository


class PomodoroService:
    """番茄钟业务：记录完成数据与统计。"""

    def __init__(self, repo: PomodoroRepository):
        self.repo = repo

    def start_session(self, habit_id: Optional[int], planned_seconds: int) -> PomodoroSession:
        """开始一个番茄计时，先返回内存对象，完成后再写库。"""
        return PomodoroSession(
            id=None,
            habit_id=habit_id,
            start_time=dt.datetime.utcnow(),
            end_time=None,
            duration_seconds=planned_seconds,
            status="running",
        )

    def complete_session(self, session: PomodoroSession, success: bool = True) -> PomodoroSession:
        session.end_time = dt.datetime.utcnow()
        session.status = "completed" if success else "aborted"
        return self.repo.add_session(session)

    def stats_today_week_month(self) -> Dict[str, int]:
        now = dt.datetime.utcnow()
        start_day = dt.datetime.combine(now.date(), dt.time.min)
        start_week = start_day - dt.timedelta(days=now.weekday())
        start_month = dt.datetime(now.year, now.month, 1)
        return {
            "today": self.repo.count_between(start_day, now),
            "this_week": self.repo.count_between(start_week, now),
            "this_month": self.repo.count_between(start_month, now),
        }
