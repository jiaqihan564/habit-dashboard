import toga
from pathlib import Path

from .repository.config_repository import ConfigRepository
from .repository.database import Database
from .repository.habit_repository import HabitRepository
from .repository.pomodoro_repository import PomodoroRepository
from .repository.record_repository import HabitRecordRepository
from .service.backup_service import BackupService
from .service.habit_service import HabitService
from .service.pomodoro_service import PomodoroService
from .service.record_service import HabitRecordService
from .service.settings_service import SettingsService
from .ui.calendar_view import CalendarView
from .ui.pomodoro_view import PomodoroView
from .ui.settings_view import SettingsView
from .ui.stats_view import StatsView
from .ui.today_view import TodayView
from .utils.i18n import t


class HabitTimerApp(toga.App):
    """应用入口：初始化依赖并拼装 UI。"""

    def startup(self):
        db_path = Path(self.paths.data) / "habit_timer.db"
        self.database = Database(db_path)

        # Repository 层
        habit_repo = HabitRepository(self.database)
        record_repo = HabitRecordRepository(self.database)
        pomodoro_repo = PomodoroRepository(self.database)
        config_repo = ConfigRepository(self.database)

        # Service 层
        self.habit_service = HabitService(habit_repo, record_repo)
        self.record_service = HabitRecordService(record_repo)
        self.pomodoro_service = PomodoroService(pomodoro_repo)
        self.settings_service = SettingsService(config_repo)
        self.backup_service = BackupService(habit_repo, record_repo, pomodoro_repo, config_repo)

        # UI
        self.stats_view = StatsView(self.habit_service, self.pomodoro_service)
        self.today_view = TodayView(
            self.habit_service, self.record_service, on_data_changed=self.refresh_views
        )
        self.pomodoro_view = PomodoroView(
            self.pomodoro_service,
            self.habit_service,
            self.settings_service,
            on_data_changed=self.refresh_views,
        )
        self.calendar_view = CalendarView(self.habit_service, self.record_service)
        self.settings_view = SettingsView(
            self.settings_service, self.backup_service, on_saved=self.refresh_views
        )

        tabs = toga.OptionContainer()
        tabs.add(t("tabs.today"), self.today_view)
        tabs.add(t("tabs.pomodoro"), self.pomodoro_view)
        tabs.add(t("tabs.calendar"), self.calendar_view)
        tabs.add(t("tabs.stats"), self.stats_view)
        tabs.add(t("tabs.settings"), self.settings_view)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = tabs
        self.main_window.show()

    def refresh_views(self):
        """数据更新后刷新依赖视图。"""
        self.stats_view.refresh_view()
        self.pomodoro_view.refresh_habits()
        self.pomodoro_view.load_default_time()
        self.calendar_view.refresh_habits()
        self.today_view.refresh_view()


def main():
    return HabitTimerApp("HabitTimer", "com.example.habit_timer")


if __name__ == "__main__":
    main().main_loop()
