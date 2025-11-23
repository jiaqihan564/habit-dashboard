import datetime as _dt
from typing import Iterable, List

# 日期相关的小工具，避免在业务逻辑中直接散落日期操作。


def today_date() -> _dt.date:
    """返回今天的日期，便于后续统一mock或扩展。"""
    return _dt.date.today()


def iso_date(date: _dt.date) -> str:
    """把日期转换为 ISO 字符串（YYYY-MM-DD）。"""
    return date.isoformat()


def parse_iso(date_str: str) -> _dt.date:
    return _dt.date.fromisoformat(date_str)


def date_range_desc(iso_dates: Iterable[str]) -> List[_dt.date]:
    """把 ISO 字符串序列转换为日期列表并按从早到晚排序。"""
    return sorted(parse_iso(d) for d in iso_dates)
