import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..service.settings_service import SettingsService


class SettingsView(toga.Box):
    """设置视图：调整番茄钟默认配置。"""

    def __init__(self, settings_service: SettingsService, on_saved=None):
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1, spacing=8))
        self.settings_service = settings_service
        self.on_saved = on_saved

        self.work_input = toga.NumberInput(min_value=1, max_value=120, style=Pack(width=100))
        self.short_input = toga.NumberInput(min_value=1, max_value=60, style=Pack(width=100))
        self.long_input = toga.NumberInput(min_value=1, max_value=180, style=Pack(width=100))
        self.interval_input = toga.NumberInput(min_value=1, max_value=10, style=Pack(width=100))

        form = toga.Box(style=Pack(direction=ROW, spacing=10))
        form.add(toga.Label("工作分钟", style=Pack(width=80)))
        form.add(self.work_input)
        form.add(toga.Label("短休", style=Pack(width=50)))
        form.add(self.short_input)
        form.add(toga.Label("长休", style=Pack(width=50)))
        form.add(self.long_input)
        form.add(toga.Label("长休间隔", style=Pack(width=70)))
        form.add(self.interval_input)

        save_btn = toga.Button("保存配置", on_press=self.save, style=Pack(padding_left=6))
        self.add(form)
        self.add(save_btn)
        self.load()

    def load(self):
        cfg = self.settings_service.get_config()
        self.work_input.value = cfg.work_minutes
        self.short_input.value = cfg.short_break_minutes
        self.long_input.value = cfg.long_break_minutes
        self.interval_input.value = cfg.long_break_interval

    def save(self, widget):
        cfg = self.settings_service.get_config()
        cfg.work_minutes = int(self.work_input.value or cfg.work_minutes)
        cfg.short_break_minutes = int(self.short_input.value or cfg.short_break_minutes)
        cfg.long_break_minutes = int(self.long_input.value or cfg.long_break_minutes)
        cfg.long_break_interval = int(self.interval_input.value or cfg.long_break_interval)
        self.settings_service.update_config(cfg)
        if self.on_saved:
            self.on_saved()
