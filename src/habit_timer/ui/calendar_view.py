import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..service.habit_service import HabitService
from ..service.record_service import HabitRecordService
from ..utils.i18n import t


class CalendarView(toga.Box):
    """最近30天完成情况的简易日历视图。"""

    def __init__(self, habit_service: HabitService, record_service: HabitRecordService):
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1))
        self.habit_service = habit_service
        self.record_service = record_service
        self.habit_options = {}

        self.habit_select = toga.Selection(style=Pack(width=250), on_change=self.on_select_change)
        self.display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))

        top = toga.Box(style=Pack(direction=ROW, padding_bottom=8))
        top.add(toga.Label(t("calendar.habit_select")))
        top.add(self.habit_select)
        self.add(top)
        self.add(self.display)
        self.refresh_habits()

    def refresh_habits(self):
        habits = self.habit_service.list_habits(enabled_only=True)
        self.habit_options = {t("calendar.no_habit"): None}
        for h in habits:
            self.habit_options[h.name] = h.id
        self.habit_select.items = list(self.habit_options.keys())
        # 设置默认选项为第一个可用选项，如果没有则设为None
        if self.habit_select.items:
            self.habit_select.value = self.habit_select.items[0]
        else:
            self.habit_select.value = None
        self.render_calendar()

    def on_select_change(self, widget):
        self.render_calendar()

    def render_calendar(self):
        habit_id = self.habit_options.get(self.habit_select.value)
        if not habit_id:
            self.display.value = t("calendar.no_data")
            return
        data = self.record_service.calendar_view(habit_id, days=30)
        lines = []
        for item in data:
            mark = "✔" if item["completed"] else "·"
            lines.append(f"{item['date']}: {mark}")
        self.display.value = "\n".join(lines)