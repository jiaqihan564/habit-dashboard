import datetime as dt
from typing import Dict, List, Tuple

from ..domain.models import Habit
from ..repository.habit_repository import HabitRepository
from ..repository.record_repository import HabitRecordRepository
from ..utils import dates


class HabitService:
    """习惯相关业务：创建/编辑/删除 + 统计计算。"""

    def __init__(self, habit_repo: HabitRepository, record_repo: HabitRecordRepository):
        self.habit_repo = habit_repo
        self.record_repo = record_repo

    def create_habit(
        self,
        name: str,
        description: str = "",
        category: str = "其它",
        target_per_week: int = 7,
        enabled: bool = True,
    ) -> Habit:
        habit = Habit(
            id=None,
            name=name,
            description=description,
            category=category,
            target_per_week=target_per_week,
            enabled=enabled,
        )
        return self.habit_repo.create(habit)

    def update_habit(self, habit: Habit) -> None:
        self.habit_repo.update(habit)

    def delete_habit(self, habit_id: int) -> None:
        # 软删除，保留历史记录，disabled 并标记 deleted_at
        self.habit_repo.soft_delete(habit_id)

    def get_habit(self, habit_id: int, include_deleted: bool = False) -> Habit | None:
        return self.habit_repo.get(habit_id, include_deleted=include_deleted)

    def list_habits(self, enabled_only: bool = False) -> List[Habit]:
        return self.habit_repo.list_all(enabled_only=enabled_only)

    def compute_streaks(self, habit_id: int) -> Tuple[int, int]:
        """计算当前连续打卡与历史最长连续打卡。

        算法：按日期升序遍历完成记录，遇到未完成或断档则重置当前连续计数。
        """
        records = self.record_repo.all_by_habit(habit_id)
        current = 0
        longest = 0
        prev_date: dt.date | None = None
        for record in records:
            if not record.is_completed:
                current = 0
                prev_date = record.date
                continue
            if prev_date and (record.date - prev_date).days == 1:
                current += 1
            else:
                current = 1
            prev_date = record.date
            longest = max(longest, current)
        return current, longest

    def recent_completion_stats(self, habit_id: int, days: int) -> Dict[str, float | int]:
        completed = self.record_repo.stats_completed_count(habit_id, days)
        return {
            "days": days,
            "completed": completed,
            "completion_rate": round(completed / days * 100, 2) if days > 0 else 0.0,
        }

    def today_status(self) -> List[Dict]:
        """返回今日需要打卡的习惯及完成状态，供 UI 展示。"""
        today = dates.today_date()
        habits = self.habit_repo.list_all(enabled_only=True)
        results = []
        for habit in habits:
            record = self.record_repo.get_by_habit_date(habit.id, today)
            results.append(
                {
                    "habit": habit,
                    "is_completed": record.is_completed if record else False,
                }
            )
        return results
