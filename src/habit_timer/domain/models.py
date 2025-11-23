from __future__ import annotations

import dataclasses
import datetime as dt
from typing import Optional

# 域模型定义：纯数据结构，不包含 UI 逻辑。


@dataclasses.dataclass
class Habit:
    """习惯定义模型。

    Attributes:
        id: 主键，自增。
        name: 习惯名称，必填。
        description: 习惯描述，可选。
        category: 分类，默认“其它”。
        target_per_week: 每周目标打卡天数（1~7）。
        enabled: 是否启用。
        created_at: 创建时间戳。
    """

    id: Optional[int]
    name: str
    description: str = ""
    category: str = "其它"
    target_per_week: int = 7
    enabled: bool = True
    created_at: dt.datetime = dataclasses.field(default_factory=dt.datetime.utcnow)


@dataclasses.dataclass
class HabitRecord:
    """习惯的每日打卡记录。"""

    id: Optional[int]
    habit_id: int
    date: dt.date
    is_completed: bool
    note: str = ""
    recorded_at: dt.datetime = dataclasses.field(default_factory=dt.datetime.utcnow)


@dataclasses.dataclass
class PomodoroSession:
    """番茄钟记录。"""

    id: Optional[int]
    habit_id: Optional[int]
    start_time: dt.datetime
    end_time: Optional[dt.datetime]
    duration_seconds: int
    status: str = "completed"  # completed/aborted


@dataclasses.dataclass
class AppConfig:
    """全局设置。"""

    id: int = 1
    work_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    long_break_interval: int = 4
