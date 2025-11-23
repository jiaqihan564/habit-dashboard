import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..service.habit_service import HabitService
from ..service.record_service import HabitRecordService


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

        self.name_input = toga.TextInput(placeholder="习惯名称", style=Pack(flex=1))
        self.category_input = toga.TextInput(placeholder="分类(可选)", style=Pack(width=120))
        self.target_input = toga.NumberInput(value=7, min_value=1, max_value=7, style=Pack(width=70))
        add_btn = toga.Button("添加习惯", on_press=self.add_habit, style=Pack(padding_left=8))

        form_row = toga.Box(
            children=[
                self.name_input,
                self.category_input,
                self.target_input,
                add_btn,
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
        self.habit_service.create_habit(name=name, category=category, target_per_week=target)
        self.name_input.value = ""
        if self.on_data_changed:
            self.on_data_changed()
        self.refresh()

    def refresh(self):
        """重新渲染习惯列表。"""
        self.list_box.children = []
        data = self.habit_service.today_status()
        if not data:
            self.list_box.add(toga.Label("还没有习惯，先添加一个吧！"))
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
                "今日完成", is_on=is_completed, on_change=self._make_toggle_handler(habit.id)
            )
            row.add(info)
            row.add(switch)
            self.list_box.add(row)

    def _make_toggle_handler(self, habit_id: int):
        def handler(widget):
            self.record_service.set_today_status(habit_id, widget.is_on)
            if self.on_data_changed:
                self.on_data_changed()
            # 立即刷新 UI，保持状态一致
            self.refresh()

        return handler
