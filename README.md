# HabitTimer

个人习惯打卡 + 番茄钟 BeeWare/Toga 示例。

## 开发

- 安装依赖：`python -m pip install -r requirements.txt`
- 本地可编辑安装（便于 `python -m habit_timer` 运行）：`python -m pip install -e .`
- 桌面调试（Briefcase）：`briefcase dev`
- 普通运行：`python -m habit_timer.main`

## 架构

- `src/habit_timer/domain`: 数据模型
- `src/habit_timer/repository`: SQLite 持久化
- `src/habit_timer/service`: 业务逻辑
- `src/habit_timer/ui`: Toga UI
- `src/habit_timer/utils/i18n.py`: 多语言资源
- 额外能力：习惯软删除、编辑、最近30天日历视图、数据导出/导入(JSON)
