# HabitTimer

个人习惯打卡 + 番茄钟 BeeWare/Toga 示例。

## 开发

- 安装依赖：`python -m pip install -r requirements.txt`（或 `pip install toga briefcase`）
- 桌面调试：`briefcase dev`
- 普通运行：`python -m habit_timer.main`

## 架构

- `src/habit_timer/domain`: 数据模型
- `src/habit_timer/repository`: SQLite 持久化
- `src/habit_timer/service`: 业务逻辑
- `src/habit_timer/ui`: Toga UI
