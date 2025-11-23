import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from ..service.settings_service import SettingsService
from ..service.backup_service import BackupService
from ..utils.i18n import t


class SettingsView(toga.Box):
    """设置视图：调整番茄钟默认配置。"""

    def __init__(self, settings_service: SettingsService, backup_service: BackupService, on_saved=None):
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1, spacing=8))
        self.settings_service = settings_service
        self.backup_service = backup_service
        self.on_saved = on_saved

        self.work_input = toga.NumberInput(min_value=1, max_value=120, style=Pack(width=100))
        self.short_input = toga.NumberInput(min_value=1, max_value=60, style=Pack(width=100))
        self.long_input = toga.NumberInput(min_value=1, max_value=180, style=Pack(width=100))
        self.interval_input = toga.NumberInput(min_value=1, max_value=10, style=Pack(width=100))

        form = toga.Box(style=Pack(direction=ROW, spacing=10))
        form.add(toga.Label(t("settings.work"), style=Pack(width=80)))
        form.add(self.work_input)
        form.add(toga.Label(t("settings.short"), style=Pack(width=50)))
        form.add(self.short_input)
        form.add(toga.Label(t("settings.long"), style=Pack(width=50)))
        form.add(self.long_input)
        form.add(toga.Label(t("settings.interval"), style=Pack(width=70)))
        form.add(self.interval_input)

        save_btn = toga.Button(t("settings.save"), on_press=self.save, style=Pack(padding_left=6))
        export_btn = toga.Button(t("settings.export"), on_press=self.export_data, style=Pack(padding_left=6))
        import_btn = toga.Button(t("settings.import"), on_press=self.import_data, style=Pack(padding_left=6))
        self.add(form)
        self.add(save_btn)
        self.add(toga.Box(children=[export_btn, import_btn], style=Pack(direction=ROW, spacing=8)))
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

    def export_data(self, widget):
        window = self.app.main_window
        dest = window.save_file_dialog(t("settings.export"), suggested_filename="habit_backup.json")
        if dest:
            try:
                self.backup_service.export_to_file(dest)
                window.info_dialog(t("settings.export"), t("dialog.export_success"))
            except Exception as exc:
                window.error_dialog(t("dialog.error"), str(exc))

    def import_data(self, widget):
        window = self.app.main_window
        src = window.open_file_dialog(t("settings.import"))
        if src:
            try:
                self.backup_service.import_from_file(src, merge_strategy="append")
                if self.on_saved:
                    self.on_saved()
                window.info_dialog(t("settings.import"), t("dialog.import_success"))
            except Exception as exc:
                window.error_dialog(t("dialog.error"), str(exc))
