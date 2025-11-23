import datetime as dt
from typing import Dict, List

from ..domain.models import HabitRecord
from ..repository.record_repository import HabitRecordRepository
from ..utils import dates


class HabitRecordService:
    """打卡相关业务，封装 UI 调用流程。"""

    def __init__(self, record_repo: HabitRecordRepository):
        self.record_repo = record_repo

    def set_today_status(self, habit_id: int, is_completed: bool, note: str = "") -> HabitRecord:
        return self.record_repo.upsert(habit_id, dates.today_date(), is_completed, note=note)

    def set_status_for_date(
        self, habit_id: int, target_date: dt.date, is_completed: bool, note: str = ""
    ) -> HabitRecord:
        return self.record_repo.upsert(habit_id, target_date, is_completed, note=note)

    def calendar_view(self, habit_id: int, days: int = 30) -> List[Dict]:
        end = dates.today_date()
        start = end - dt.timedelta(days=days - 1)
        records = self.record_repo.fetch_by_habit_and_range(habit_id, start, end)
        by_date = {dates.iso_date(r.date): r for r in records}
        view = []
        for i in range(days):
            d = start + dt.timedelta(days=i)
            iso = dates.iso_date(d)
            record = by_date.get(iso)
            view.append({"date": iso, "completed": record.is_completed if record else False})
        return view
