import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from ..service.habit_service import HabitService
from ..service.pomodoro_service import PomodoroService
from ..utils.i18n import t


class StatsView(toga.Box):
    """统计概览视图，使用文本展示。

    注意：避免覆盖 Toga 的 refresh（会与子控件刷新递归）。改用 refresh_view。
    """

    def __init__(self, habit_service: HabitService, pomodoro_service: PomodoroService):
        # 先保存依赖，避免 Box 初始化过程中触发父类 refresh 时属性未就绪
        self.habit_service = habit_service
        self.pomodoro_service = pomodoro_service
        self.output = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        super().__init__(style=Pack(direction=COLUMN, padding=10, flex=1))
        self.add(self.output)
        self.refresh_view()

    def refresh_view(self):
        """刷新统计数据文本，避免与 Toga 内部 refresh 互相递归。"""
        lines = []
        lines.append(t("stats.habit"))
        habits = self.habit_service.list_habits(enabled_only=True)
        if not habits:
            lines.append(t("stats.none"))
        for h in habits:
            current, longest = self.habit_service.compute_streaks(h.id)
            stat7 = self.habit_service.recent_completion_stats(h.id, 7)
            stat30 = self.habit_service.recent_completion_stats(h.id, 30)
            lines.append(
                f"- {h.name} 连续:{current}/{longest} | 7天:{stat7['completed']}/{stat7['days']} ({stat7['completion_rate']}%) | 30天:{stat30['completed']}/{stat30['days']} ({stat30['completion_rate']}%)"
            )

        p_stats = self.pomodoro_service.stats_today_week_month()
        lines.append(f"\n{t('stats.pomodoro')}")
        lines.append(
            f"今天: {p_stats['today']} 个 | 本周: {p_stats['this_week']} 个 | 本月: {p_stats['this_month']} 个"
        )
        # 直接设置 value（多行文本本身会刷新子控件，不再触发父类 refresh）
        self.output.value = "\n".join(lines)
