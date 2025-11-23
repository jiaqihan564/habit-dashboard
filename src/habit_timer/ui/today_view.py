import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..domain.models import Habit
from ..service.habit_service import HabitService
from ..service.record_service import HabitRecordService
from ..utils.i18n import t


class TodayView(toga.Box):
    """今日习惯视图，负责展示及打卡 UI 调用流程。"""

    def __init__(
        self,
        habit_service: HabitService,
        record_service: HabitRecordService,
        on_data_changed=None,
    ):
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1))
        self.habit_service = habit_service
        self.record_service = record_service
        self.on_data_changed = on_data_changed
        self.list_box = toga.Box(style=Pack(direction=COLUMN, spacing=8))
        self.editing_habit_id = None

        self.name_input = toga.TextInput(placeholder=t("today.name"), style=Pack(flex=1))
        self.category_input = toga.TextInput(placeholder=t("today.category"), style=Pack(width=120))
        self.target_input = toga.NumberInput(value=7, min_value=1, max_value=7, style=Pack(width=70))
        self.add_btn = toga.Button(t("today.add"), on_press=self.add_habit, style=Pack(padding_left=8))

        form_row = toga.Box(
            children=[
                self.name_input,
                self.category_input,
                self.target_input,
                self.add_btn,
            ],
            style=Pack(direction=ROW, spacing=8, padding_bottom=6),
        )

        self.add(form_row)
        self.scroll = toga.ScrollContainer(content=self.list_box, style=Pack(flex=1))
        self.add(self.scroll)
        self.refresh()

    def add_habit(self, widget):
        name = self.name_input.value.strip()
        if not name:
            return
        category = self.category_input.value.strip() or "其它"
        target = int(self.target_input.value or 7)
        if self.editing_habit_id:
            habit = self.habit_service.get_habit(self.editing_habit_id)
            if habit:
                habit.name = name
                habit.category = category
                habit.target_per_week = target
                self.habit_service.update_habit(habit)
        else:
            self.habit_service.create_habit(name=name, category=category, target_per_week=target)
        self.name_input.value = ""
        self.category_input.value = ""
        self.editing_habit_id = None
        self.add_btn.text = t("today.add")
        if self.on_data_changed:
            self.on_data_changed()
        self.refresh()

    def refresh(self):
        """重新渲染习惯列表。"""
        self.list_box.children = []
        data = self.habit_service.today_status()
        if not data:
            self.list_box.add(toga.Label(t("today.no_habit")))
            return

        for item in data:
            habit = item["habit"]
            is_completed = item["is_completed"]
            current_streak, longest_streak = self.habit_service.compute_streaks(habit.id)

            row = toga.Box(style=Pack(direction=ROW, alignment="center", spacing=8))
            info = toga.Label(
                f"{habit.name} [{habit.category}] 目标/周:{habit.target_per_week} | 连续:{current_streak}/{longest_streak}",
                style=Pack(flex=1),
            )
            switch = toga.Switch(
                t("today.complete"), is_on=is_completed, on_change=self._make_toggle_handler(habit.id)
            )
            edit_btn = toga.Button(t("today.edit"), on_press=self._make_edit_handler(habit), style=Pack(width=60))
            delete_btn = toga.Button(t("today.delete"), on_press=self._make_delete_handler(habit.id), style=Pack(width=60))
            row.add(info)
            row.add(switch)
            row.add(edit_btn)
            row.add(delete_btn)
            self.list_box.add(row)

    def _make_toggle_handler(self, habit_id: int):
        def handler(widget):
            self.record_service.set_today_status(habit_id, widget.is_on)
            if self.on_data_changed:
                self.on_data_changed()
            # 立即刷新 UI，保持状态一致
            self.refresh()

        return handler

    def _make_edit_handler(self, habit: Habit):
        def handler(widget):
            self.editing_habit_id = habit.id
            self.name_input.value = habit.name
            self.category_input.value = habit.category
            self.target_input.value = habit.target_per_week
            self.add_btn.text = t("today.save")

        return handler

    def _make_delete_handler(self, habit_id: int):
        def handler(widget):
            self.habit_service.delete_habit(habit_id)
            if self.on_data_changed:
                self.on_data_changed()
            self.refresh()

        return handler
