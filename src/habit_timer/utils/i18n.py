"""简单的多语言资源管理。

后续可以扩展为从 JSON/YAML 读取，或根据系统语言切换。
"""

LANG = "zh"

STRINGS = {
    "zh": {
        "tabs.today": "今日打卡",
        "tabs.pomodoro": "番茄钟",
        "tabs.stats": "统计",
        "tabs.settings": "设置",
        "tabs.calendar": "日历",
        "today.add": "添加习惯",
        "today.save": "保存修改",
        "today.no_habit": "还没有习惯，先添加一个吧！",
        "today.name": "习惯名称",
        "today.category": "分类(可选)",
        "today.target": "目标/周",
        "today.complete": "今日完成",
        "today.edit": "编辑",
        "today.delete": "删除",
        "calendar.habit_select": "选择习惯",
        "calendar.no_habit": "请选择习惯",
        "calendar.no_data": "暂无数据",
        "pomodoro.none": "无关联",
        "pomodoro.start": "开始番茄",
        "pomodoro.pause": "暂停/继续",
        "pomodoro.stop": "结束",
        "pomodoro.link": "关联习惯",
        "pomodoro.status.idle": "未开始",
        "pomodoro.status.running": "番茄进行中",
        "pomodoro.status.paused": "已暂停",
        "pomodoro.status.resume": "继续计时",
        "pomodoro.status.finished": "完成",
        "pomodoro.status.stopped": "已结束",
        "stats.habit": "【习惯统计】",
        "stats.none": "暂无习惯",
        "stats.pomodoro": "【番茄统计】",
        "settings.save": "保存配置",
        "settings.work": "工作分钟",
        "settings.short": "短休",
        "settings.long": "长休",
        "settings.interval": "长休间隔",
        "settings.export": "导出数据",
        "settings.import": "导入数据(追加)",
        "dialog.export_success": "导出成功",
        "dialog.import_success": "导入成功",
        "dialog.error": "错误",
    },
    "en": {
        "tabs.today": "Today",
        "tabs.pomodoro": "Pomodoro",
        "tabs.stats": "Stats",
        "tabs.settings": "Settings",
        "tabs.calendar": "Calendar",
        "today.add": "Add",
        "today.save": "Save",
        "today.no_habit": "No habits yet, add one!",
        "today.name": "Habit name",
        "today.category": "Category(optional)",
        "today.target": "Target/wk",
        "today.complete": "Today Done",
        "today.edit": "Edit",
        "today.delete": "Delete",
        "calendar.habit_select": "Habit",
        "calendar.no_habit": "Select a habit",
        "calendar.no_data": "No data",
        "pomodoro.none": "None",
        "pomodoro.start": "Start",
        "pomodoro.pause": "Pause/Resume",
        "pomodoro.stop": "Stop",
        "pomodoro.link": "Linked Habit",
        "pomodoro.status.idle": "Idle",
        "pomodoro.status.running": "Running",
        "pomodoro.status.paused": "Paused",
        "pomodoro.status.resume": "Resume",
        "pomodoro.status.finished": "Finished",
        "pomodoro.status.stopped": "Stopped",
        "stats.habit": "[Habit Stats]",
        "stats.none": "No habits",
        "stats.pomodoro": "[Pomodoro Stats]",
        "settings.save": "Save",
        "settings.work": "Work(min)",
        "settings.short": "Short break",
        "settings.long": "Long break",
        "settings.interval": "Long break interval",
        "settings.export": "Export data",
        "settings.import": "Import data(append)",
        "dialog.export_success": "Exported",
        "dialog.import_success": "Imported",
        "dialog.error": "Error",
    },
}


def set_lang(lang: str):
    global LANG
    if lang in STRINGS:
        LANG = lang


def t(key: str, **kwargs) -> str:
    lang_dict = STRINGS.get(LANG, STRINGS["zh"])
    text = lang_dict.get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text
