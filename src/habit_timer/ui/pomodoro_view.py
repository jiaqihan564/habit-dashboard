import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..domain.models import PomodoroSession
from ..service.habit_service import HabitService
from ..service.pomodoro_service import PomodoroService
from ..service.settings_service import SettingsService


class PomodoroView(toga.Box):
    """番茄钟视图，包含状态机与非阻塞计时器。"""

    def __init__(
        self,
        pomodoro_service: PomodoroService,
        habit_service: HabitService,
        settings_service: SettingsService,
        on_data_changed=None,
    ):
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1))
        self.pomodoro_service = pomodoro_service
        self.habit_service = habit_service
        self.settings_service = settings_service
        self.on_data_changed = on_data_changed

        self.state = "idle"  # idle -> running -> paused -> finished
        self.remaining_seconds = 0
        self.timer = None
        self.active_session: PomodoroSession | None = None
        self.habit_options = {"无关联": None}

        self.habit_select = toga.Selection(items=["无关联"], style=Pack(width=200))
        self.time_label = toga.Label("00:00", style=Pack(font_size=36, padding_bottom=8))
        self.status_label = toga.Label("未开始", style=Pack(padding_bottom=8))

        start_btn = toga.Button("开始番茄", on_press=self.start, style=Pack(padding=4))
        pause_btn = toga.Button("暂停/继续", on_press=self.toggle_pause, style=Pack(padding=4))
        stop_btn = toga.Button("结束", on_press=self.stop, style=Pack(padding=4))

        self.add(
            toga.Box(
                children=[toga.Label("关联习惯"), self.habit_select],
                style=Pack(direction=ROW, spacing=8, padding_bottom=8),
            )
        )
        self.add(self.time_label)
        self.add(self.status_label)
        self.add(
            toga.Box(
                children=[start_btn, pause_btn, stop_btn],
                style=Pack(direction=ROW, spacing=8),
            )
        )

        self.refresh_habits()
        self.load_default_time()

    def load_default_time(self):
        cfg = self.settings_service.get_config()
        self.remaining_seconds = cfg.work_minutes * 60
        self._update_time_label()

    def refresh_habits(self):
        habits = self.habit_service.list_habits(enabled_only=True)
        self.habit_options = {"无关联": None}
        for h in habits:
            self.habit_options[h.name] = h.id
        self.habit_select.items = list(self.habit_options.keys())
        self.habit_select.value = "无关联"

    def start(self, widget):
        if self.state == "running":
            return
        cfg = self.settings_service.get_config()
        self.remaining_seconds = cfg.work_minutes * 60
        habit_id = self.habit_options.get(self.habit_select.value)
        self.active_session = self.pomodoro_service.start_session(
            habit_id=habit_id, planned_seconds=self.remaining_seconds
        )
        self.state = "running"
        self.status_label.text = "番茄进行中"
        self._start_timer()

    def toggle_pause(self, widget):
        if self.state == "running":
            self.state = "paused"
            self.status_label.text = "已暂停"
            if self.timer:
                self.timer.cancel()
        elif self.state == "paused":
            self.state = "running"
            self.status_label.text = "继续计时"
            self._start_timer()

    def stop(self, widget):
        if self.state in ["running", "paused"]:
            self._finish_session(success=False)

    def _start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = toga.Timer(1.0, self._tick, repeat=True)
        self.timer.start()

    def _tick(self, timer):
        if self.state != "running":
            return
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self._finish_session(success=True)
        self._update_time_label()

    def _finish_session(self, success: bool):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        if self.active_session:
            self.pomodoro_service.complete_session(self.active_session, success=success)
        self.state = "finished"
        self.status_label.text = "完成" if success else "已结束"
        if self.on_data_changed:
            self.on_data_changed()
        self.load_default_time()
        self.state = "idle"
        self.active_session = None

    def _update_time_label(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.time_label.text = f"{minutes:02d}:{seconds:02d}"
